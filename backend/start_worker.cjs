const path = require('path');
const { spawn } = require('child_process');

const pythonBin = path.join(__dirname, 'venv', 'Scripts', 'python.exe');

const proc = spawn(
  pythonBin,
  ['scraper_worker.py', '--loop'],
  { cwd: __dirname, stdio: 'inherit', windowsHide: true }
);

proc.on('close', (code) => process.exit(code));
