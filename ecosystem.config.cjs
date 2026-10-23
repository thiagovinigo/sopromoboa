module.exports = {
  apps: [
    {
      name: 'sopromo-3000',
      cwd: './frontend',
      script: 'node_modules/next/dist/bin/next',
      args: 'dev -p 3000',
      interpreter: 'C:/Program Files/nodejs/node.exe',
      env: { NODE_ENV: 'development', NEXT_PUBLIC_API_URL: 'http://localhost:8001' }
    },
    {
      name: 'sopromo-8001',
      cwd: './backend',
      script: 'start.cjs',
      interpreter: 'C:/Program Files/nodejs/node.exe',
      env: { PYTHONUNBUFFERED: '1', PORT: '8001' }
    },
    {
      name: 'sopromo-worker',
      cwd: './backend',
      script: 'start_worker.cjs',
      interpreter: 'C:/Program Files/nodejs/node.exe',
      env: { PYTHONUNBUFFERED: '1' }
    }
  ]
};
