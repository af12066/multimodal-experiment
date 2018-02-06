# calibration

眼電図キャリブレーションタスク実行スクリプト。提示部は Node.js + [Electron](https://electronjs.org)、記録部は Python 3.x で動きます。

### Installation

```bash
$ yarn install
```

または

```bash
$ npm install
```

し、さらに

```bash
$ ./node_modules/.bin/electron-rebuild
```

を実行します。ただし、`electron-rebuild` に Python 2.x が必要です。

## Usage

Windows の場合は、エクスプローラで `main.bat` を実行すれば記録スクリプトと提示スクリプトが走ります。

## Author

Takuma Hashimoto (<ma16079@shibaura-it.ac.jp>)
