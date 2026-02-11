# SenseiPlus

为sensei们提供的额外的[CET](https://github.com/Wangs-official/CodemaoEDUTools)功能

## 如何使用？

请在开始使用前运行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

## 使用Nuitka构建成exe

请使用以下命令构建

注意：第一次构建可能非常慢，因为CodemaoEDUTools使用了Pandas库

```bash
nuitka --standalone --jobs=auto --follow-imports --include-package=CodemaoEDUTools --include-package-data=fake_useragent --include-data-file=MenuLite/Menu/MlConfig.json=MenuLite/Menu/MlConfig.json --include-data-file=build_info.json=build_info.json --output-dir=dist --output-filename=SenseiPlus Main.py
```

## 免责声明

> [!CAUTION]
> 我只是把这些库拼接在了一起，用的永远是你的Token，不是我的 ，出啥事了也与我无关。
>
> 还请分清界限，也别给我举报到官方去，你要真想让编程猫变好，不如先从自己开始变好。

## 贡献

我们非常欢迎您为SenseiPlus提交贡献，您可以通过以下方式贡献：

- 提交Pull Request（PR）
- 报告问题（Issue）
- 建议新功能（Feature Request）
- 改进文档（Documentation）
