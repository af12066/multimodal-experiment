/*
 * 注視点キャリブレーション用スクリプト (Electron)
 * 
 * Electron で HTML を描画するところをやります。
 * 描画するロジックは script.js で書いています。
 */
'use strict';

const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;
const ipc = electron.ipcMain;
const serialport = require('serialport');

let mainWindow = null;

const portName = 'COM6'
const sp = new serialport(portName, {
  baudRate: 9600,
  dataBits: 8,
  parity: 'none',
  flowControl: false,
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('ready', () => {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    fullscreen: true,
    frame: false,
    webPreferences: {
      nodeIntegration: true
    }
  });
  // mainWindow.openDevTools();
  mainWindow.loadURL('file://' + __dirname + '/index.html');

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
});

// シリアルポートが正常にオープンしたときの処理
// この中で ipc を待機させる
sp.on('open', () => {
  setTimeout(() => {
    ipc.on('synchronous-message', (event, arg) => {
      console.log("arg: ", arg);
      sp.write(new Buffer(arg));
      event.returnValue = "Okay";
    });
  }, 2000);
});

// シリアルポート周りでエラーが起きたら終了
sp.on('error', () => {
  process.exit(1);
});
