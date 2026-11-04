# Cloudflare Pages 部署

GitHub Pages 與 Cloudflare Pages 都由 `main` 分支建置，內容相同，差別只在網址的基底路徑。Cloudflare 專案尚未建立，建立後把網址補進下表。

| 項目 | 值 |
|---|---|
| 網址 | 待建立 |
| 部署方式 | Git integration，GitHub App 只授權這個 repo |
| Production branch | `main` |
| Build command | `bundle exec jekyll build --baseurl ""` |
| Build output | `_site` |
| Ruby | `.ruby-version` 指定 3.4.4，與 Cloudflare 建置映像的預設版本相同 |

## 為什麼這樣設定

`_config.yml` 的 `baseurl: /robot-notes` 是給 GitHub Pages 用的，因為它的網址在子路徑底下。Cloudflare Pages 的站台在網域根目錄，所以建置指令用 `--baseurl ""` 覆寫，兩邊共用同一份設定檔。

Cloudflare 需要 `Gemfile` 才知道要裝哪些套件。GitHub Pages 不讀這個檔，因此不受影響。`Gemfile` 釘住與 GitHub Pages 相同的 `github-pages` 套件，讓兩邊的 Jekyll 版本與外掛一致。

`_config.yml` 的 `exclude` 是自訂清單，會蓋掉 Jekyll 的預設排除，所以 `Gemfile`、`Gemfile.lock`、`vendor/` 要自己列。

## 只有版控內的檔案會上線

Git integration 從 GitHub 取得原始碼，`.gitignore` 內的 `tmp/`、`talk_record/`、`slam/` 不會進入建置。不要在本機工作樹建站後手動上傳：工作樹內有這些不公開的檔案。

## 依據

Cloudflare 官方文件，2026-11-04 查閱：

- [Jekyll 框架指南](https://developers.cloudflare.com/pages/framework-guides/deploy-a-jekyll-site/)：建置指令與輸出目錄。
- [從 GitHub Pages 遷移 Jekyll](https://developers.cloudflare.com/pages/migrations/migrating-jekyll-from-github-pages/)：需要 `Gemfile`。
- [Build image](https://developers.cloudflare.com/pages/configuration/build-image/)：預設 Ruby 版本與 `.ruby-version` 覆寫。
- [Limits](https://developers.cloudflare.com/pages/platform/limits/)：單站檔案數與單檔大小上限。
- [Workers best practices](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/)：官方建議新專案用 Workers Static Assets，Pages 仍可使用。本站沿用 Pages 的 Git integration，推送後自動建置。
