# Pyxel SameGame

[ [English](README.md) | [日本語](README.ja.md) ]

Pyxel を使って作成されたシンプルなさめがめ風パズルゲームです。同じ色のブロックが繋がった部分を消していき、盤面をクリアすることを目指します。このプロジェクトは、生成AIの力を借りて24時間でどこまでゲームを作れるか挑戦した結果生まれたものです。

## 特徴
- **クラシックなパズル**: シンプルながら奥深い「さめがめ」のゲーム性。
- **レトロなスタイル**: Pyxel を使った懐かしい8ビット風のデザイン。
- **動的なBGM**: [8bit BGM Generator](https://github.com/shiromofufactory/8bit-bgm-generator) を活用して、毎回異なるBGMを生成。
- **HTMLで簡単プレイ**: ブラウザで直接遊べる手軽さ。

## ゲームをプレイ
**こちらからプレイ:** [Pyxel SameGame - GitHub Pages](https://hnsol.github.io/pyxel-samegame/pyxelsg.html)

## 遊び方
- マウスまたはスマホのタップで、同じ色のブロックが繋がった部分を選択して消します。
- 一度に多くのブロックを消すと高得点を獲得。
- すべてのブロックを消すことを目指しましょう。消せるブロックがなくなるとゲーム終了です。

## インストール方法
1. **ブラウザで遊ぶ**:
   上記のリンクをクリックして、すぐにプレイを開始できます。

2. **ローカルで実行**:
   ```bash
   git clone https://github.com/hnsol/pyxel-samegame.git
   cd pyxel-samegame
   pyxel run pyxelsg/pyxelsg.py
   ```

   Pyxel のインストールが必要です:
   ```bash
   pip install pyxel
   ```

## スクリーンショット
![ゲームプレイのスクリーンショット](https://cdn-ak.f.st-hatena.com/images/fotolife/m/masatora_bd5/20250114/20250114225440.gif)

## 技術的なポイント
- **盤面生成**: 解くことが可能な盤面を生成する独自アルゴリズム。
- **動的BGM**: [8bit BGM Generator](https://github.com/shiromofufactory/8bit-bgm-generator) を利用してプレイ中に生成される音楽。

## クレジット
- **開発者**: [hann-solo](https://github.com/hnsol)
- **BGM Generator**: [しろもふファクトリー](https://github.com/shiromofufactory)

## 参考情報
- [Pyxel公式サイト](https://github.com/kitao/pyxel)
- [Qiitaのアドベントカレンダー記事：ほとんど手でコードを書かずにPyxelのゲームを作ろうとした話](https://qiita.com/hann-solo/items/e417c29c22d008752f60)

## ストーリー

東洋には、108の煩悩を消せば（滅却すれば）、悟りの境地に至れるという伝説がある。
長きにわたり、現代社会の喧騒とデジタル世界に疲れ果てた人々は、その伝説に希望を見出した。
さめがめの盤面に広がる色と形。その一つひとつのブロックが、心の中に潜む煩悩を象徴しているかのようだ。
果たしてあなたは、全ての煩悩を打ち破り、安らぎを手に入れることができるのか——。

## SAME

このプロジェクトの名称 "SAME" には、以下の意味を込めています：

### **日本語アクロニム**
- **さ）とりを め）ざして が）んばれ め）っきゃく**

### **英語アクロニム**
- **SAME: Surrender Attachments, Mindfulness, and Enlightenment**

### **クウェンヤアクロニム**
- **SAME: Sere Atara, Melme, Eruanna**
  - **Sere**（平和、安らぎ）
  - **Atara**（父、高貴な存在の象徴）
  - **Melme**（愛、情熱）
  - **Eruanna**（恩寵、悟りに至る贈り物）

### 全体のコンセプト

日本語、英語、クウェンヤの各アクロニムが、それぞれの言語と文化的背景に合わせて、「悟りを目指し、努力と自己超越を通じて煩悩を手放し、平和と恩寵に至る精神的道」を表現しています。それぞれが同じ理念を異なる方法で体現しています。

## ライセンス
このプロジェクトは MIT ライセンスの下で公開されています。詳細は LICENSE ファイルをご覧ください。

---

「シンプルイズベスト」– このゲームと同じく、実用的で簡潔に。
