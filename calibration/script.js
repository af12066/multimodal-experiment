/*
 * 注視点キャリブレーション用スクリプト
 * 
 * CSS を更新することで、注視点をずらしながら順番に点灯させていきます。
 * HTML で jQuery を読み込んだ後にこのスクリプトを読み込んでください。
 */
$(function() {
  let row = 0;
  let col = 0;
  let send_trigger = false; // Arduino に送信する注視点変更時のトリガ．
  let intvl;
  // 注視点のx座標を指定する
  const x = [
    '384px',
    '768px',
    '1152px',
    '1536px'
  ];
  // 注視点のy座標を指定する
  const y = [
    '216px',
    '432px',
    '648px',
    '864px',
  ];

  function settrig(){
    clearInterval(intvl);
    // 注視点移動の時間を設定し、tgl を実行
    intvl = setInterval(tgl, 5000);
  }

  function tgl(){
    send_trigger = !send_trigger;
    synchronous(Number(send_trigger).toString());  // ipc 経由で Arduino に数値としてシリアルで送信
    if (col === 4) {
      // 注視点の点灯終了
      $('.rectangle').toggle();
      $('.target').hide();
      clearInterval(intvl);
      return;
    }
    $('.rectangle').toggle();
    $('.target').css('left', x[row]);
    $('.target').css('top', y[col]);
    $('.target').show();
    if (row === 3) {
      col++;
      row = 0;
    } else {
      row++;
    }
  }

  $(document).ready(function(){
    // 初期状態はなにもない状態
    $('.target').hide();
    // ウィンドウをクリックしたときに実験開始
    $(window).click(function(){
      settrig();
    });
  });
});
