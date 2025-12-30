# チケットサービス - Vercelデプロイガイド

このFlaskアプリケーションをVercelにデプロイする方法を説明します。

## 📋 前提条件

- [Vercel](https://vercel.com)のアカウント
- [Vercel CLI](https://vercel.com/docs/cli)のインストール（オプション）

## 🚀 デプロイ手順

### 方法1: Vercel CLI を使用

1. Vercel CLIをインストール:
```bash
npm install -g vercel
```

2. プロジェクトディレクトリで以下を実行:
```bash
vercel
```

3. 初回は質問に答えてプロジェクトを設定します
4. デプロイが完了すると、URLが表示されます

### 方法2: GitHub経由でデプロイ

1. このプロジェクトをGitHubリポジトリにプッシュ
2. [Vercel Dashboard](https://vercel.com/dashboard)にログイン
3. "New Project"をクリック
4. GitHubリポジトリを選択
5. "Deploy"をクリック

## ⚙️ 設定ファイル

以下のファイルがVercelデプロイ用に設定されています:

- **vercel.json**: Vercelの設定ファイル
- **api/index.py**: サーバーレス関数のエントリーポイント
- **requirements.txt**: Python依存関係

## ⚠️ 重要な注意事項

### データの永続化について

Vercelのサーバーレス環境では、`/tmp`ディレクトリのデータは一時的です。
本番環境では、以下のいずれかを使用してデータを永続化することを推奨します:

1. **Vercel KV** (Redis互換のキーバリューストア)
2. **Vercel Postgres** (PostgreSQLデータベース)
3. **外部データベース** (MongoDB Atlas, Supabaseなど)

### 現在の制限事項

- データは`/tmp`に保存されるため、サーバーレス関数の実行間で失われる可能性があります
- HTTPSは自動的にVercelによって提供されます
- 証明書ファイル(cert.pem, key.pem)は不要です

## 🔧 本番環境への改善案

データベースを使用する場合の例（Vercel Postgres）:

```python
# api/index.pyに追加
import psycopg2
from urllib.parse import urlparse

# 環境変数からデータベースURLを取得
DATABASE_URL = os.environ.get('POSTGRES_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)
```

## 📝 環境変数の設定

Vercel Dashboardで以下の環境変数を設定できます:

1. プロジェクトの設定に移動
2. "Environment Variables"タブを選択
3. 必要な変数を追加（例: データベース接続情報）

## 🌐 デプロイ後

デプロイが成功すると、以下のようなURLでアクセスできます:
- `https://your-project.vercel.app/` - メインページ
- `https://your-project.vercel.app/organizer` - 主催者ページ
- `https://your-project.vercel.app/admin` - 管理者ページ

## 🐛 トラブルシューティング

デプロイに問題がある場合:

1. Vercelのログを確認: `vercel logs`
2. ビルドログをVercel Dashboardで確認
3. `requirements.txt`の依存関係を確認

## 📚 参考リンク

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)
