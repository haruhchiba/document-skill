# 参考スライド選定

## 目的

ローカルライブラリの364枚を全件採点し、各出力スライドの役割に合う構造候補を3〜5枚へ絞る。候補は目視比較してから採用する。

## カテゴリ

| `primary_category` | 用途 |
|---|---|
| `title-divider` | 表紙、章扉 |
| `agenda-overview` | 目次、全体像 |
| `bullet-summary` | 課題、特徴、まとめ |
| `card-columns` | 機能、メリット、施策 |
| `comparison-matrix` | 比較、選択肢 |
| `concept-diagram` | 課題整理、関係図、全体像 |
| `process-roadmap` | 導入フロー、手順 |
| `timeline-roadmap` | 計画、沿革 |
| `kpi-highlight` | 導入効果、実績 |
| `chart` | 分析、数値説明 |
| `table-matrix` | 機能一覧、情報整理 |
| `hierarchy` | 優先度、成熟度 |
| `device-mockup` | 製品画面、機能紹介 |
| `profile-case` | 会社紹介、事例 |
| `cta-closing` | 問い合わせ、クロージング |
| `general-content` | 上記に当てはまらない本文 |

## 採点仕様

`reference-score-spec.json` は出力スライドごとの狙いを定義する。

```json
{
  "slides": [
    {
      "slide": 1,
      "role": "表紙",
      "primary_categories": ["title-divider"],
      "layout_families": ["title-or-section-divider"],
      "preferred_tags": ["minimal", "spacious"],
      "avoid_tags": ["dark-background"],
      "visual_targets": {
        "white_ratio": 0.7,
        "edge_density": 4.0
      }
    }
  ]
}
```

不要な条件は省略できる。カテゴリとレイアウトを中心に指定し、数値特徴は明確な意図がある場合だけ使う。

## 出力

`score_reference_library.py` は以下を生成する。

- `reference-score-all.csv`: 全参考画像 x 全出力スライド
- `reference-shortlist.json`: 各出力スライドの上位候補

`make_candidate_contact_sheets.py` は `reference-shortlist.json` から比較画像を生成する。

`resolve_reference_library.py` はローカルライブラリの配置先を解決する。探索順は次の通り。

1. `--library-dir`
2. 環境変数 `DOCUMENT_SKILL_REFERENCE_LIBRARY`
3. ローカル設定ファイル `~/.codex/document-skill-reference-library.txt` の1行目
4. 現在の作業フォルダと親フォルダ周辺
5. このskillと同じ作業領域の周辺

公開リポジトリへ参考画像を追加しない。

PowerShell で日本語を含むパスを変数へ渡す場合は、標準出力を直接取り込まず `--out-file` でUTF-8ファイルへ書き出してから `Get-Content -Encoding utf8` で読む。

## 採用基準

- 情報量が出力内容に合うか
- 余白と視線誘導が明快か
- 図解や比較軸が内容を正しく伝えるか
- `interpark-pptx` のブランド規則で自然に再実装できるか
- 元画像固有の写真、ロゴ、装飾に依存していないか

## 構造観察

採用候補を決める前に、画像を目視し、次を `reference-selection-audit.md` に記録する。観察結果は選択肢であり、複製要件ではない。

- 列数と行数
- タイトル、本文、図表、画像の占有領域
- 左から右、上から下などの読み順
- 主役となる領域と、その面積感
- 余白の位置
- 完成資料へ借りたい要素
- 借りない要素と、その理由
- 独自に追加したい要素と、その理由

カテゴリ一致は候補抽出にだけ使う。採用後は、参考構造をそのまま複製するのではなく、内容を最も明快に伝えられるかを判断する。1枚の参考画像から全要素を借りる必要はない。写真やロゴを転用できない場合は、編集可能な図解、プレースホルダー、または余白へ置き換える。

構造を変更する場合は、変更点と改善理由を `reference-selection-audit.md` に記録する。たとえば、図表を大きく見せるために見出しを縮小する、説明が3点なら列構造を整理する、読み順を明確にするために余白を調整する、といった変更は許容する。

## 見出しの判断

見出し、英字ラベル、補足文は必須ではない。次を基準に採否を決める。

- 見出しがなくても図表の意味が一目で分かる場合は、省略または小型化する。
- 図表の読み方や結論を先に示す必要がある場合は、短い主張見出しを置く。
- 小さな共通ヘッダーバーがページ識別に十分な場合は、大見出しを追加しない。
- 大見出しを置く場合は、図表や写真の主役領域を圧迫していないか確認する。
- `WORKFLOW` などの英字ラベルは、階層の理解を速める場合だけ使う。

## 構成QA

完成PNGと採用参考PNGを並べて確認する。

- 参考画像から借りた構造が、内容の理解に役立っているか
- スライドの主役となる図表やメッセージに十分な面積があるか
- 読み順が明快か
- 共通ヘッダー、見出し、ラベルが主役を圧迫していないか
- 元画像の固有素材を転用していないか
- ブランド規則による変更が読みやすさを損ねていないか

参考構造を変更した場合は、変更理由が説明できるか確認する。説明できない変更は見直す。参考画像へ近づけること自体を目的にしない。
