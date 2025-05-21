# EzInterview

This repository is a course project for CS160 Human Computer Interaction at
ShanghaiTech University.

Author: 万宇昂、叶卿、刘兆骋、胡崮斌、钱嘉烨

## Usage

### 后端

后端基于 Python，请确保使用的 Python 版本为 **3.9 或更高**。

1. 安装 [Python](https://www.python.org/downloads/)

2. 进入后端目录：

   ```bash
   cd backend
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

4. 启动后端服务：

   ```bash
   python main.py
   ```

### 前端

前端采用 Node.js 与 Vue 构建。以下以 `interviewee` 界面为例：

1. 安装 [Node.js](https://nodejs.org/zh-cn)

   > ⚠️ 注意：在 Windows 系统中，通过 Node.js 图形安装程序安装时，安装向导 **默认勾选了安装 Chocolatey**。如果你勾选此选项，安装过程可能会自动安装或修改系统中的 Python 环境，**可能导致原有非虚拟环境下的 Python 被覆盖或路径冲突**。
   > 为避免此问题，建议在安装 Node.js 时 **取消勾选安装 Chocolatey 的选项**。

2. 进入前端目录：

   ```bash
   cd frontends/interviewee
   ```

3. 安装 Vue 和其他依赖：

   ```bash
   npm install
   ```

4. 构建生产版本并本地预览：

   ```bash
   npm run build
   cd dist
   npx serve
   ```

   然后在浏览器中输入弹出的网页链接进行预览
