(() => {
  "use strict";

  const params = new URLSearchParams(window.location.search);
  const token = params.get("token") || "";
  const shouldAutoplay = params.get("autoplay") !== "0";
  const socketProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const socketUrl = `${socketProtocol}//${window.location.host}/obs-widget/socket?${new URLSearchParams({ token })}`;

  const widget = document.getElementById("radioWidget");
  const title = document.getElementById("title");
  const artist = document.getElementById("artist");
  const elapsed = document.getElementById("elapsed");
  const duration = document.getElementById("duration");
  const progressFill = document.getElementById("progressFill");
  const progressKnob = document.getElementById("progressKnob");
  const statusLabel = document.getElementById("statusLabel");

  let socket = null;
  let reconnectDelay = 350;
  let currentRadio = null;
  let receivedAt = 0;
  let autoplayRequested = false;

  const clamp = (value, minimum, maximum) => Math.max(minimum, Math.min(maximum, value));

  const formatTime = (value) => {
    const seconds = Math.max(0, Math.floor(Number(value) || 0));
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainder = seconds % 60;
    return hours > 0
      ? `${hours}:${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`
      : `${minutes}:${String(remainder).padStart(2, "0")}`;
  };

  const setMarquee = (element) => {
    element.classList.remove("is-marquee");
    window.requestAnimationFrame(() => {
      const viewport = element.parentElement;
      if (viewport && element.scrollWidth > viewport.clientWidth + 10) {
        element.classList.add("is-marquee");
      }
    });
  };

  const sendCommand = (command) => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    socket.send(JSON.stringify({
      command,
      request_id: `radio-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    }));
  };

  const render = () => {
    const radio = currentRadio || {};
    const ready = Boolean(radio.ready && radio.title);
    const playing = Boolean(ready && radio.playing);
    const durationSeconds = Math.max(0, Number(radio.duration_seconds) || 0);
    let elapsedSeconds = Math.max(0, Number(radio.elapsed_seconds) || 0);
    if (playing && receivedAt) {
      elapsedSeconds += Math.max(0, performance.now() - receivedAt) / 1000;
    }
    if (durationSeconds > 0) elapsedSeconds = Math.min(durationSeconds, elapsedSeconds);
    const progress = durationSeconds > 0
      ? clamp(elapsedSeconds / durationSeconds, 0, 1)
      : clamp(Number(radio.progress) || 0, 0, 1);

    widget.classList.toggle("is-waiting", !ready);
    widget.classList.toggle("is-playing", playing);
    widget.classList.toggle("is-paused", ready && !playing);

    const nextTitle = ready ? radio.title : "SMW Central Radio";
    const nextArtist = ready
      ? (radio.artist || radio.details || "SMW Central Music Library")
      : "Waiting for the tracker…";
    if (title.textContent !== nextTitle) {
      title.textContent = nextTitle;
      setMarquee(title);
    }
    if (artist.textContent !== nextArtist) {
      artist.textContent = nextArtist;
      setMarquee(artist);
    }
    elapsed.textContent = ready ? formatTime(elapsedSeconds) : "0:00";
    duration.textContent = ready
      ? (radio.duration || formatTime(durationSeconds))
      : "0:00";
    const progressPercentage = `${(progress * 100).toFixed(3)}%`;
    progressFill.style.width = progressPercentage;
    progressKnob.style.left = progressPercentage;
    statusLabel.textContent = playing ? "ON AIR" : (ready ? "PAUSED" : "CONNECTING");

    window.requestAnimationFrame(render);
  };

  const connect = () => {
    socket = new WebSocket(socketUrl);
    socket.addEventListener("open", () => {
      reconnectDelay = 350;
      if (shouldAutoplay && !autoplayRequested) {
        autoplayRequested = true;
        sendCommand("radio_start");
      }
    });
    socket.addEventListener("message", (event) => {
      let document;
      try { document = JSON.parse(event.data); } catch (_error) { return; }
      if (!document || typeof document !== "object" || !document.radio) return;
      currentRadio = document.radio;
      receivedAt = performance.now();
    });
    socket.addEventListener("close", () => {
      socket = null;
      autoplayRequested = false;
      window.setTimeout(connect, reconnectDelay);
      reconnectDelay = Math.min(5000, Math.round(reconnectDelay * 1.65));
    });
    socket.addEventListener("error", () => socket?.close());
  };

  window.addEventListener("resize", () => {
    setMarquee(title);
    setMarquee(artist);
  });
  connect();
  window.requestAnimationFrame(render);
})();
