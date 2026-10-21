const path = require('path');
const { spawn } = require('child_process');

const pythonBin = path.join(__dirname, 'venv', 'Scripts', 'python.exe');

const proc = spawn(
  pythonBin,
  ['-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8001', '--reload'],
  { cwd: __dirname, stdio: 'inherit', windowsHide: true }
);

proc.on('close', (code) => process.exit(code));
