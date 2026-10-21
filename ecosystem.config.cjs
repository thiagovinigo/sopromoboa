module.exports = {
  apps: [
    {
      name: 'sopromo-3000',
      cwd: './frontend',
      script: 'node_modules/next/dist/bin/next',
      args: 'dev -p 3000',
      interpreter: 'C:/Program Files/nodejs/node.exe',
      env: { NODE_ENV: 'development' }
    },
    {
      name: 'sopromo-8001',
      cwd: './backend',
      script: 'start.cjs',
      interpreter: 'C:/Program Files/nodejs/node.exe',
      env: { PYTHONUNBUFFERED: '1', PORT: '8001' }
    }
  ]
};
