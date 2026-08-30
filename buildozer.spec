[app]

# 应用名称（安卓桌面上显示的名字）
title = 24点游戏

# 包名（改成自己的，如 com.yourname.game24）
package.name = game24
package.domain = org.example

# 源码目录与需要打包进 APK 的文件类型（注意包含字体 otf）
source.dir = .
source.include_exts = py,otf,ttf,png,jpg,kv

# 版本号
version = 1.0.0

# 依赖
# Python 固定 3.12.8：p4a 默认 3.14 与 kivy 2.3.0 + Cython 0.29 不兼容，且 python3/hostpython3 版本必须一致
requirements = python3==3.12.8,hostpython3==3.12.8,kivy==2.3.0

# 竖屏
orientation = portrait
fullscreen = 0

# Android 构建参数
android.api = 31
# Python 3.12 需要 API 26+（getgrent/setgrent/endgrent 从 API 26 才提供）
android.minapi = 26
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.ndk = 25c
android.ndk_path = /home/runner/.buildozer/android/platform/android-ndk-r25c
android.ndk_api = 26

# 保留通知等默认设置
android.accept_sdk_license = True

# 应用内部存储目录名
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

[buildozer]

# 日志级别 2=info
log_level = 2

# 警告计数
warn_on_root = 1

# 构建缓存目录
# 必须保持隐藏目录（点开头）：buildozer 复制源码时会自动跳过隐藏目录，
# 否则 ./build 会被复制进 APK 私有数据，compileall 会因第三方源码中的
# Python 2 脚本（如 SDL2_image 的 versiongenerate.py）报语法错误
build_dir = ./.buildozer
