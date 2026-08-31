param(
    [string]$ToolchainRoot = "",
    [string]$SourceDirectory = "Main_MiSTer_20260816_custom",
    [string]$BuildVersion = "SMWEXP"
)

$ErrorActionPreference = "Stop"
$experimentRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceRoot = Join-Path $experimentRoot $SourceDirectory
$workspaceRoot = Resolve-Path (Join-Path $experimentRoot "..\..\..\..\..")

if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot "Makefile"))) {
    throw "MiSTer source folder was not found: $sourceRoot"
}
if ($BuildVersion -notmatch "^[A-Za-z0-9]{6}$") {
    throw "BuildVersion must contain exactly six letters or digits."
}

if (-not $ToolchainRoot) {
    $toolchain = Get-ChildItem -LiteralPath (Join-Path $workspaceRoot ".toolchains") -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "bin\arm-none-linux-gnueabihf-gcc.exe") } |
        Select-Object -First 1
    if (-not $toolchain) {
        throw "The Arm cross-compiler was not found under $workspaceRoot\.toolchains."
    }
    $ToolchainRoot = $toolchain.FullName
}

$buildRoot = Join-Path $sourceRoot "bin_experimental"
New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null

# The official Windows-hosted Arm toolchain has legacy path-length behavior.
# A temporary drive mapping keeps every compiler/sysroot path short and is
# removed in the finally block even when compilation fails.
$drive = "T:"
$existingMapping = (subst.exe) | Where-Object { $_ -match "^T:" }
if ($existingMapping) {
    throw "Drive T: is already mapped. Remove that mapping or change the drive in this script."
}

subst.exe $drive $ToolchainRoot
try {
    $cc = "$drive\bin\arm-none-linux-gnueabihf-gcc.exe"
    $ld = "$drive\bin\arm-none-linux-gnueabihf-ld.exe"
    $strip = "$drive\bin\arm-none-linux-gnueabihf-strip.exe"

    $includes = @(
        "-I$sourceRoot",
        "-I$(Join-Path $sourceRoot 'lib\libco')",
        "-I$(Join-Path $sourceRoot 'lib\miniz')",
        "-I$(Join-Path $sourceRoot 'lib\md5')",
        "-I$(Join-Path $sourceRoot 'lib\lzma')",
        "-I$(Join-Path $sourceRoot 'lib\zstd\lib')",
        "-I$(Join-Path $sourceRoot 'lib\libchdr\include')",
        "-I$(Join-Path $sourceRoot 'lib\bluetooth')",
        "-I$(Join-Path $sourceRoot 'lib\serial_server\library')"
    )
    $defines = @(
        "-D_7ZIP_ST",
        '-DPACKAGE_VERSION="1.3.3"',
        "-DHAVE_LROUND",
        "-DHAVE_STDINT_H",
        "-DHAVE_STDLIB_H",
        "-DHAVE_SYS_PARAM_H",
        "-DENABLE_64_BIT_WORDS=0",
        "-D_FILE_OFFSET_BITS=64",
        "-D_LARGEFILE64_SOURCE",
        "-DVDATE=`"$BuildVersion`""
    )
    $warnings = @(
        "-Wall", "-Wextra", "-Wno-strict-aliasing", "-Wno-stringop-overflow",
        "-Wno-stringop-truncation", "-Wno-format-truncation", "-Wno-psabi",
        "-Wno-restrict"
    )
    $common = $includes + $defines + $warnings + @("-O3", "-c")

    $cSources = @()
    $cSources += Get-ChildItem -LiteralPath $sourceRoot -Filter "*.c" -File
    foreach ($relative in @("lib\miniz", "lib\md5", "lib\lzma", "lib\zstd\lib\common", "lib\zstd\lib\decompress", "lib\libchdr")) {
        $cSources += Get-ChildItem -LiteralPath (Join-Path $sourceRoot $relative) -Filter "*.c" -File
    }
    $cSources += Get-Item -LiteralPath (Join-Path $sourceRoot "lib\libco\arm.c")

    $cppSources = @()
    $cppSources += Get-ChildItem -LiteralPath $sourceRoot -Filter "*.cpp" -File
    $serialServer = Join-Path $sourceRoot "lib\serial_server\library"
    if (Test-Path -LiteralPath $serialServer) {
        $cppSources += Get-ChildItem -LiteralPath $serialServer -Filter "*.cpp" -File
    }
    foreach ($supportDir in Get-ChildItem -LiteralPath (Join-Path $sourceRoot "support") -Directory) {
        $cppSources += Get-ChildItem -LiteralPath $supportDir.FullName -Filter "*.cpp" -File
    }

    $objects = [System.Collections.Generic.List[string]]::new()

    Push-Location $sourceRoot
    try {
        foreach ($source in $cSources) {
            $relative = [IO.Path]::GetRelativePath($sourceRoot, $source.FullName)
            $object = Join-Path $buildRoot ($relative + ".o")
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $object) | Out-Null
            Write-Host "Compiling $relative"
            & $cc @common "-std=gnu99" "-o" $object $relative
            if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $relative" }
            $objects.Add($object)
        }

        foreach ($source in $cppSources) {
            $relative = [IO.Path]::GetRelativePath($sourceRoot, $source.FullName)
            $object = Join-Path $buildRoot ($relative + ".o")
            New-Item -ItemType Directory -Force -Path (Split-Path -Parent $object) | Out-Null
            Write-Host "Compiling $relative"
            & $cc @common "-std=gnu++14" "-Wno-class-memaccess" "-o" $object $relative
            if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $relative" }
            $objects.Add($object)
        }

        foreach ($image in Get-ChildItem -LiteralPath $sourceRoot -Filter "*.png" -File) {
            $relative = $image.Name
            $object = Join-Path $buildRoot ($relative + ".o")
            Write-Host "Embedding $relative"
            & $ld "-r" "-b" "binary" "-o" $object $relative
            if ($LASTEXITCODE -ne 0) { throw "Resource embedding failed: $relative" }
            $objects.Add($object)
        }

        $output = Join-Path $buildRoot "MiSTer-SMW-Virtual-States"
        $response = Join-Path $buildRoot "objects.rsp"
        [IO.File]::WriteAllLines($response, ($objects | ForEach-Object { $_.Replace('\', '/') }))

        Write-Host "Linking experimental MiSTer binary"
        $linkArgs = @(
            "-o", $output, "@$response", "-lc", "-lstdc++", "-lm", "-lrt",
            "-Llib/imlib2", "-lfreetype", "-lbz2", "-lpng16", "-lz", "-lImlib2",
            "-Llib/bluetooth", "-lbluetooth", "-lpthread"
        )
        & $cc @linkArgs
        if ($LASTEXITCODE -ne 0) { throw "Linking the experimental MiSTer binary failed." }

        Copy-Item -LiteralPath $output -Destination ($output + ".elf") -Force
        & $strip $output
        if ($LASTEXITCODE -ne 0) { throw "Stripping the experimental MiSTer binary failed." }

        Get-FileHash -Algorithm SHA256 -LiteralPath $output
    }
    finally {
        Pop-Location
    }
}
finally {
    subst.exe $drive /D | Out-Null
}
