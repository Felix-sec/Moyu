## 🐟摸鱼提醒小助手
原本在NGCBot实现的功能，现移植过来的

## 🔧安装与配置
- ### 安装依赖
  确保你的Python环境已经安装以下依赖库：
  ```python
  pip install Pillow zhdate
  ```
- ### 配置文件
  在 `plugins/Moyu` 目录下创建 `config.toml` 文件，并进行如下配置：
  ```bash
  [Moyu]
  enable = true
  commands = ["摸鱼", "摸鱼提醒", "提醒摸鱼", "摸鱼小助手"]
  priority = 60
  ```
  配置项说明：
  - `enable`：是否启用该插件，`true`为启用，`false`为禁用。
  - `commands`：触发插件功能的命令列表，用户输入这些命令时，插件会做出相应处理。
  - `priority`：支持设置插件的优先级，数值越高优先级越高，默认应为60。

## 📝使用说明
直接发送 `摸鱼`、`摸鱼提醒`、`摸鱼小助手` 等指令即可触发，无需at机器人