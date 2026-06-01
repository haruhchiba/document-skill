---
name: document-skill
description: インターパークの営業資料・提案資料・サービス紹介資料をPowerPoint形式で新規作成または改修するスキル。「資料を作って」「提案書を作成」「営業資料」「サービス紹介スライド」「参考スライドを基に構成して」などの依頼で使う。`interpark-pptx` の文字・配色・ブランド規則を正本として採用し、ローカルの参考スライドライブラリから用途別に構成候補を比較して、編集可能なPPTXを作る。
---

# インターパーク資料作成

## 位置づけ

`presentations` skill と `interpark-pptx` skill を併用する。

- `presentations`: PPTX生成、レンダリング、視覚QAの技術手順
- `interpark-pptx`: 文字、配色、余白、ヘッダー、フッター、ロゴ配置の正本
- このskill: 内容設計、参考スライド選定、構成への反映、選定記録

参考画像は編集可能なPPTXテンプレートではない。画像を背景として貼り付けず、元画像の文言、社名、人物写真、ロゴを転用しない。構造だけを参考にして再実装する。

## 作成判断

依頼内容を確認し、次の順で進める。

1. 既存PPTXの軽微修正なら `presentations` の targeted-edit を使う。
2. ユーザー提供PPTXを忠実に継承するなら `presentations` の template-following を使う。
3. 新規資料、構成見直し、参考スライドを基にした再設計なら、このskillの参考選定フローを使う。

構成探しを始める前に、サービス、対象読者、利用場面、伝えたい結論、必須情報、想定ページ数を整理する。不明点が成果物を大きく変える場合だけ確認する。

## 作業領域

`presentations` skill の thread-scoped workspace 規則に従う。以下を追加で使う。

```text
$LIBRARY_DIR/
$WORKSPACE/reference-selection/
```

参考ライブラリは公開リポジトリへ同梱しない。以下でローカルの配置先を解決する。

```powershell
$LIBRARY_PATH_FILE = "$WORKSPACE\reference-selection\library-path.txt"
python "$SKILL_DIR\scripts\resolve_reference_library.py" --out-file "$LIBRARY_PATH_FILE"
$LIBRARY_DIR = (Get-Content -LiteralPath "$LIBRARY_PATH_FILE" -Encoding utf8 -Raw).Trim()
```

見つからない場合は、ユーザーへ配置先を確認する。明示する場合は `--library-dir` を使うか、環境変数 `DOCUMENT_SKILL_REFERENCE_LIBRARY` を設定する。ローカル設定ファイル `~/.codex/document-skill-reference-library.txt` がある場合は、その1行目も候補として使う。

参考ライブラリの概要は `$LIBRARY_DIR/REFERENCE.md` を読む。採点仕様とカテゴリ選択の詳細が必要な場合は `references/reference-selection.md` を読む。

## ワークフロー

### 1. 内容を設計する

参考スライドを探す前に、資料全体の主張と各スライドの役割を決める。

- 1スライド1メッセージにする。
- 各スライドに claim、根拠、見せ方を定義する。
- 表紙、課題、解決策、機能、比較、導入フロー、効果、事例、クロージングなど、必要な役割だけを採用する。
- 情報不足を装飾で埋めない。

`$WORKSPACE/claim-spine.txt` に資料全体の流れを残す。

### 2. 参考候補を全件採点する

各出力スライドの役割を `$WORKSPACE/reference-selection/reference-score-spec.json` に定義する。仕様例は `references/reference-selection.md` を参照する。

```powershell
python "$SKILL_DIR\scripts\score_reference_library.py" `
  --catalog "$LIBRARY_DIR\catalog.csv" `
  --spec "$WORKSPACE\reference-selection\reference-score-spec.json" `
  --out-dir "$WORKSPACE\reference-selection" `
  --top-k 5
```

必ず `catalog.csv` の364行すべてを採点する。先頭数枚だけで決めない。

### 3. 候補を目視比較する

```powershell
python "$SKILL_DIR\scripts\make_candidate_contact_sheets.py" `
  --shortlist "$WORKSPACE\reference-selection\reference-shortlist.json" `
  --library-dir "$LIBRARY_DIR" `
  --out-dir "$WORKSPACE\reference-selection\contact-sheets"
```

各スライドの上位3〜5候補を比較する。採点結果だけで自動決定せず、採用候補の `slides/NNN.png` を開いて確認する。

`$WORKSPACE/reference-selection/reference-selection-audit.md` に以下を残す。

- 出力スライド番号と役割
- 比較した参考ID
- 採用した参考ID
- 採用理由
- 構造観察: 列、行、主役領域、読み順、密度、余白
- 完成資料へ借りる要素
- 借りない要素と、その理由
- 独自に追加する要素と、その理由
- 反映しない要素

### 4. ブランド規則で再実装する

`interpark-pptx` を読み、色、文字、ヘッダー、フッター、ロゴ配置を適用する。

- 参考画像から借りるのは、情報の並べ方、余白、強弱、視線誘導、図解の型だけにする。
- 参考画像のブランド表現より `interpark-pptx` を優先する。
- ロゴ、人物、製品画面はユーザー提供または出典確認済みの素材だけを使う。
- PPTXは編集可能な要素で作る。参考PNGを完成スライドの背景にしない。
- 参考画像は構造の出発点として使う。主役領域、列数、行数、読み順を確認したうえで、内容がより明快になる場合は変更してよい。
- 参考構造を変更する場合は、`reference-selection-audit.md` に変更点と改善理由を残す。カテゴリ一致だけで採用を完了しない。
- 見出しや共通要素が主役の図表を圧迫する場合は、見出しを短くする、省略する、図表内へ統合するなど、資料として伝わりやすい構成を優先する。
- 見出し、英字ラベル、補足文は必須要素ではない。スライドの理解を速める場合だけ使う。
- 小さなヘッダーバーと大きな主張見出しを機械的に併置しない。情報階層を増やす効果が薄い場合は、どちらか一方にする。

### 5. レンダリングして確認する

`presentations` skill の手順でPPTXをレンダリングし、完成資料のコンタクトシートを作る。

- サムネイルで資料全体のリズムを確認する。
- 各ページで文字切れ、重なり、余白不足、読みにくい小文字を確認する。
- 参考画像と完成PNGを見比べ、構造の良さが残っているか確認する。
- 採用した参考PNGと完成PNGを並べ、参考構造から借りた要素、意図的に変えた要素、変更によって読みやすくなった点を確認する。
- ブランド規則と構成参考が衝突した場合は、ブランド規則を優先する。

## 必須成果物

最終PPTXに加えて、作業領域に以下を残す。

- `claim-spine.txt`
- `reference-selection/reference-score-spec.json`
- `reference-selection/reference-score-all.csv`
- `reference-selection/reference-shortlist.json`
- `reference-selection/reference-selection-audit.md`
- `reference-selection/contact-sheets/slide-XX-candidates.jpg`

## ライブラリ更新

参考ライブラリを差し替える場合は、ローカルライブラリの `catalog.csv`、`catalog.json`、`REFERENCE.md`、`contact_sheets/`、`slides/`、`thumbnails/` を同時に更新する。索引と画像を片方だけ更新しない。公開リポジトリへ参考画像を追加しない。
