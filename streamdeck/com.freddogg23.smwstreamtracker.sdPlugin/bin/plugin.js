"use strict";

const crypto = require("crypto");
const fs = require("fs");
const net = require("net");
const os = require("os");
const path = require("path");

const PLUGIN_UUID = "com.freddogg23.smwstreamtracker";
const DEFAULT_TRACKER_PORT = 18765;
const CONFIG_PATH = path.join(os.homedir(), "SMWStreamTrackerConfig.json");
const ACTIONS = Object.freeze({
  start: `${PLUGIN_UUID}.radio-start`,
  close: `${PLUGIN_UUID}.radio-close`,
  toggle: `${PLUGIN_UUID}.radio-toggle`,
  restart: `${PLUGIN_UUID}.radio-restart`,
  next: `${PLUGIN_UUID}.radio-next`,
  loop: `${PLUGIN_UUID}.radio-loop`,
  seekBack: `${PLUGIN_UUID}.radio-seek-back`,
  seekForward: `${PLUGIN_UUID}.radio-seek-forward`,
  volumeDown: `${PLUGIN_UUID}.radio-volume-down`,
  volumeUp: `${PLUGIN_UUID}.radio-volume-up`,
});

function parseArguments(argv) {
  const result = {};
  for (let index = 2; index < argv.length; index += 1) {
    const item = String(argv[index] || "");
    if (!item.startsWith("-")) continue;
    const key = item.replace(/^-+/, "");
    const value = argv[index + 1];
    if (value !== undefined && !String(value).startsWith("-")) {
      result[key] = String(value);
      index += 1;
    } else {
      result[key] = "true";
    }
  }
  return result;
}

function websocketAccept(key) {
  return crypto
    .createHash("sha1")
    .update(`${key}258EAFA5-E914-47DA-95CA-C5AB0DC85B11`, "ascii")
    .digest("base64");
}

class LocalWebSocket {
  constructor(urlText, handlers = {}) {
    this.url = new URL(urlText);
    this.handlers = handlers;
    this.socket = null;
    this.buffer = Buffer.alloc(0);
    this.handshakeComplete = false;
    this.ready = false;
    this.closed = false;
    this.closeReported = false;
    this.fragmentOpcode = null;
    this.fragments = [];
    this.key = crypto.randomBytes(16).toString("base64");
  }

  connect() {
    const port = Number(this.url.port || 80);
    this.socket = net.createConnection({
      host: this.url.hostname,
      port,
    });
    this.socket.setNoDelay(true);
    this.socket.on("connect", () => this._sendHandshake());
    this.socket.on("data", (chunk) => this._receive(chunk));
    this.socket.on("error", (error) => this._finish(error));
    this.socket.on("close", () => this._finish());
    return this;
  }

  _sendHandshake() {
    const requestPath = `${this.url.pathname || "/"}${this.url.search || ""}`;
    const host = `${this.url.hostname}:${this.url.port || 80}`;
    const request = [
      `GET ${requestPath} HTTP/1.1`,
      `Host: ${host}`,
      "Upgrade: websocket",
      "Connection: Upgrade",
      `Sec-WebSocket-Key: ${this.key}`,
      "Sec-WebSocket-Version: 13",
      "",
      "",
    ].join("\r\n");
    this.socket.write(request, "ascii");
  }

  _receive(chunk) {
    if (this.closed) return;
    this.buffer = Buffer.concat([this.buffer, Buffer.from(chunk)]);
    if (!this.handshakeComplete && !this._consumeHandshake()) return;
    this._consumeFrames();
  }

  _consumeHandshake() {
    const marker = this.buffer.indexOf("\r\n\r\n");
    if (marker < 0) return false;
    const headerText = this.buffer.subarray(0, marker).toString("utf8");
    this.buffer = this.buffer.subarray(marker + 4);
    const lines = headerText.split("\r\n");
    const status = lines.shift() || "";
    const headers = {};
    for (const line of lines) {
      const colon = line.indexOf(":");
      if (colon <= 0) continue;
      headers[line.slice(0, colon).trim().toLowerCase()] = line
        .slice(colon + 1)
        .trim();
    }
    if (
      !/^HTTP\/1\.[01] 101\b/.test(status) ||
      headers["sec-websocket-accept"] !== websocketAccept(this.key)
    ) {
      this._finish(new Error(`WebSocket upgrade failed: ${status}`));
      return false;
    }
    this.handshakeComplete = true;
    this.ready = true;
    if (typeof this.handlers.open === "function") this.handlers.open();
    return true;
  }

  _consumeFrames() {
    while (this.buffer.length >= 2 && !this.closed) {
      const first = this.buffer[0];
      const second = this.buffer[1];
      const finished = Boolean(first & 0x80);
      const opcode = first & 0x0f;
      const masked = Boolean(second & 0x80);
      let payloadLength = second & 0x7f;
      let headerLength = 2;
      if (payloadLength === 126) {
        if (this.buffer.length < 4) return;
        payloadLength = this.buffer.readUInt16BE(2);
        headerLength = 4;
      } else if (payloadLength === 127) {
        if (this.buffer.length < 10) return;
        const largeLength = this.buffer.readBigUInt64BE(2);
        if (largeLength > BigInt(Number.MAX_SAFE_INTEGER)) {
          this._finish(new Error("WebSocket frame is too large"));
          return;
        }
        payloadLength = Number(largeLength);
        headerLength = 10;
      }
      const maskLength = masked ? 4 : 0;
      const totalLength = headerLength + maskLength + payloadLength;
      if (this.buffer.length < totalLength) return;
      let payload = Buffer.from(
        this.buffer.subarray(headerLength + maskLength, totalLength)
      );
      if (masked) {
        const mask = this.buffer.subarray(headerLength, headerLength + 4);
        for (let index = 0; index < payload.length; index += 1) {
          payload[index] ^= mask[index % 4];
        }
      }
      this.buffer = this.buffer.subarray(totalLength);
      if (opcode === 0x8) {
        this.close();
        return;
      }
      if (opcode === 0x9) {
        this._writeFrame(payload, 0x0a);
        continue;
      }
      if (opcode === 0x0a) continue;
      if (opcode === 0x0) {
        if (this.fragmentOpcode === null) continue;
        this.fragments.push(payload);
        if (finished) {
          this._emitPayload(this.fragmentOpcode, Buffer.concat(this.fragments));
          this.fragmentOpcode = null;
          this.fragments = [];
        }
        continue;
      }
      if (!finished) {
        this.fragmentOpcode = opcode;
        this.fragments = [payload];
        continue;
      }
      this._emitPayload(opcode, payload);
    }
  }

  _emitPayload(opcode, payload) {
    if (opcode !== 0x1 || typeof this.handlers.message !== "function") return;
    this.handlers.message(payload.toString("utf8"));
  }

  _writeFrame(payloadValue, opcode = 0x1) {
    if (!this.socket || this.socket.destroyed || !this.handshakeComplete) return false;
    const payload = Buffer.isBuffer(payloadValue)
      ? payloadValue
      : Buffer.from(String(payloadValue), "utf8");
    const mask = crypto.randomBytes(4);
    let header;
    if (payload.length < 126) {
      header = Buffer.from([0x80 | opcode, 0x80 | payload.length]);
    } else if (payload.length <= 0xffff) {
      header = Buffer.alloc(4);
      header[0] = 0x80 | opcode;
      header[1] = 0x80 | 126;
      header.writeUInt16BE(payload.length, 2);
    } else {
      header = Buffer.alloc(10);
      header[0] = 0x80 | opcode;
      header[1] = 0x80 | 127;
      header.writeBigUInt64BE(BigInt(payload.length), 2);
    }
    const maskedPayload = Buffer.alloc(payload.length);
    for (let index = 0; index < payload.length; index += 1) {
      maskedPayload[index] = payload[index] ^ mask[index % 4];
    }
    this.socket.write(Buffer.concat([header, mask, maskedPayload]));
    return true;
  }

  send(document) {
    if (!this.ready) return false;
    return this._writeFrame(JSON.stringify(document), 0x1);
  }

  close() {
    if (this.closed) return;
    try {
      if (this.ready) this._writeFrame(Buffer.alloc(0), 0x8);
    } catch (_error) {}
    this._finish();
  }

  _finish(error) {
    if (this.closed) return;
    this.closed = true;
    this.ready = false;
    if (this.socket && !this.socket.destroyed) this.socket.destroy();
    if (!this.closeReported && typeof this.handlers.close === "function") {
      this.closeReported = true;
      this.handlers.close(error);
    }
  }
}

const argumentsMap = parseArguments(process.argv);
const streamDeckPort = Number(argumentsMap.port || 0);
const pluginUUID = argumentsMap.pluginUUID || PLUGIN_UUID;
const registerEvent = argumentsMap.registerEvent || "registerPlugin";

let streamDeckSocket = null;
let trackerSocket = null;
let trackerReconnectTimer = null;
let trackerReconnectDelay = 500;
let latestRadioState = {};
let shuttingDown = false;
const visibleContexts = new Map();
const pendingCommands = new Map();

function sendToStreamDeck(event, context, payload = {}) {
  if (!streamDeckSocket || !streamDeckSocket.ready) return;
  const document = { event };
  if (context) document.context = context;
  if (payload !== undefined) document.payload = payload;
  streamDeckSocket.send(document);
}

function showResult(context, ok) {
  sendToStreamDeck(ok ? "showOk" : "showAlert", context, {});
}

function updateKeyStates() {
  const playingState = latestRadioState.playing ? 1 : 0;
  const loopingState = latestRadioState.looping ? 1 : 0;
  for (const [context, action] of visibleContexts.entries()) {
    if (action === ACTIONS.toggle) {
      sendToStreamDeck("setState", context, { state: playingState });
    } else if (action === ACTIONS.loop) {
      sendToStreamDeck("setState", context, { state: loopingState });
    }
  }
}

function readTrackerConnection() {
  let config = {};
  try {
    const raw = fs.readFileSync(CONFIG_PATH, "utf8").replace(/^\uFEFF/, "");
    config = JSON.parse(raw);
  } catch (_error) {}
  const configuredPort = Number(config.obs_widget_port || DEFAULT_TRACKER_PORT);
  const port = Number.isInteger(configuredPort) && configuredPort > 0 && configuredPort < 65536
    ? configuredPort
    : DEFAULT_TRACKER_PORT;
  const token = String(config.obs_widget_access_token || "");
  return {
    port,
    token,
  };
}

function scheduleTrackerReconnect() {
  if (shuttingDown || trackerReconnectTimer) return;
  trackerReconnectTimer = setTimeout(() => {
    trackerReconnectTimer = null;
    connectToTracker();
  }, trackerReconnectDelay);
  trackerReconnectDelay = Math.min(5000, Math.round(trackerReconnectDelay * 1.55));
}

function connectToTracker() {
  if (shuttingDown || (trackerSocket && !trackerSocket.closed)) return;
  const connection = readTrackerConnection();
  const query = new URLSearchParams({ token: connection.token }).toString();
  trackerSocket = new LocalWebSocket(
    `ws://127.0.0.1:${connection.port}/obs-widget/socket?${query}`,
    {
      open: () => {
        trackerReconnectDelay = 500;
      },
      message: handleTrackerMessage,
      close: () => {
        trackerSocket = null;
        scheduleTrackerReconnect();
      },
    }
  ).connect();
}

function handleTrackerMessage(message) {
  let document;
  try {
    document = JSON.parse(message);
  } catch (_error) {
    return;
  }
  if (!document || typeof document !== "object") return;
  if (document.radio && typeof document.radio === "object") {
    latestRadioState = { ...document.radio };
    updateKeyStates();
  }
  if (document.event === "command_result") {
    const requestID = String(document.request_id || "");
    const context = pendingCommands.get(requestID);
    if (context) {
      pendingCommands.delete(requestID);
      showResult(context, Boolean(document.ok));
    }
  }
}

function commandForAction(action) {
  if (action === ACTIONS.start) return { command: "radio_start" };
  if (action === ACTIONS.close) return { command: "radio_close" };
  if (action === ACTIONS.toggle) return { command: "radio_toggle" };
  if (action === ACTIONS.restart) return { command: "radio_restart" };
  if (action === ACTIONS.next) return { command: "radio_next" };
  if (action === ACTIONS.loop) return { command: "radio_loop" };
  if (action === ACTIONS.seekBack) {
    return { command: "radio_seek", delta_seconds: -10 };
  }
  if (action === ACTIONS.seekForward) {
    return { command: "radio_seek", delta_seconds: 10 };
  }
  if (action === ACTIONS.volumeDown) {
    return { command: "radio_volume", delta: -10 };
  }
  if (action === ACTIONS.volumeUp) {
    return { command: "radio_volume", delta: 10 };
  }
  return null;
}

function runAction(action, context) {
  const command = commandForAction(action);
  if (!command) return;
  if (!trackerSocket || !trackerSocket.ready) {
    showResult(context, false);
    if (!trackerSocket || trackerSocket.closed) connectToTracker();
    return;
  }
  const requestID = `streamdeck-${Date.now()}-${crypto.randomBytes(4).toString("hex")}`;
  command.request_id = requestID;
  pendingCommands.set(requestID, context);
  if (!trackerSocket.send(command)) {
    pendingCommands.delete(requestID);
    showResult(context, false);
    return;
  }
  setTimeout(() => pendingCommands.delete(requestID), 4000);
}

function handleStreamDeckMessage(message) {
  let document;
  try {
    document = JSON.parse(message);
  } catch (_error) {
    return;
  }
  if (!document || typeof document !== "object") return;
  const event = String(document.event || "");
  const context = String(document.context || "");
  const action = String(document.action || "");
  if (event === "willAppear" && context) {
    visibleContexts.set(context, action);
    updateKeyStates();
  } else if (event === "willDisappear" && context) {
    visibleContexts.delete(context);
  } else if (event === "keyDown" && context) {
    runAction(action, context);
  }
}

function connectToStreamDeck() {
  if (!Number.isInteger(streamDeckPort) || streamDeckPort <= 0) {
    process.exitCode = 2;
    return;
  }
  streamDeckSocket = new LocalWebSocket(
    `ws://127.0.0.1:${streamDeckPort}/`,
    {
      open: () => {
        streamDeckSocket.send({
          event: registerEvent,
          uuid: pluginUUID,
        });
        connectToTracker();
      },
      message: handleStreamDeckMessage,
      close: () => {
        shutdown();
        process.exit(0);
      },
    }
  ).connect();
}

function shutdown() {
  if (shuttingDown) return;
  shuttingDown = true;
  if (trackerReconnectTimer) clearTimeout(trackerReconnectTimer);
  trackerReconnectTimer = null;
  if (trackerSocket) trackerSocket.close();
  if (streamDeckSocket) streamDeckSocket.close();
}

process.on("SIGINT", () => {
  shutdown();
  process.exit(0);
});
process.on("SIGTERM", () => {
  shutdown();
  process.exit(0);
});
process.on("exit", shutdown);

connectToStreamDeck();
