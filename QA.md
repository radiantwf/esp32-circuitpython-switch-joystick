# 常见问题汇总

## 设备选择

   ```text
Q: 我该选择什么型号单片机？XXXX单片机是否可以使用？
A: 原则上 [固件下载链接](https://circuitpython.org/downloads) 包含的设备都可以使用。
我测试过的设备包含：LOLIN S2 Mini、ESP32-S3-DevKitC-1-N16R8、Raspberry Pi Pico (W)。
其中LOLIN S2 Mini有10%左右的网友购买后刷入circuitpython固件后，PC无法识别，猜测是渠道的硬件问题，请大家谨慎选购。
   ```

   ```text
Q: 能否提供单片机的购买链接？
A: 抱歉，由于我也没有单片机购买渠道，所以我无法对购买商铺进行任何推荐，请大家自行寻找靠谱选购。
   ```

   ```text
Q: 我该使用什么连接线？
A: 随便一款手机数据线都可以支持，不过Switch端请不要使用Type-C直接连接，请使用底座或OTG转接口，直接连接可能会有主从识别问题。
（我自己的Type-c To Type-c 的线无法正常连接单片机，无法确定是否是线的问题）
   ```

## 固件刷写

   ```text
Q: 7.3.3版本固件与8.0.0-beta版本固件我该选择哪一个？
A: 如果你对开发有一定了解，并有使用TCP网络远程控制的需求，建议使用7.3.3版本固件。
   新手建议直接使用8.0.0-beta版本固件，8.0.0-beta版本固件，请自行 [固件下载链接](https://circuitpython.org/downloads) 寻找对应设备下载。
   ```

   ```text
Q: 我想刷写7.3.3版固件，我该刷写哪一个文件？能否使用官网的官方固件？
A: 由于7.3.3版本固件限制，必须针对不同设备进行修改再次编译，才能使用，所以如果没有专业的技能不建议使用。
   其中LOLIN S2 Mini与ESP32-S3-DevKitC-1-N16R8我提供了编译好的版本。
   以LOLIN S2 Mini为例，请刷写 "firmware/circuitpython/7.3.3/lolin-s2-mini/switch_pro/firmware_7.3.3.bin" 固件文件。
   ```

   ```text
Q: RP2040芯片（Raspberry Pi Pico等）的单片机如何刷写固件？
A: 请参照设备官网提供的方式进行固件刷写操作。
   ```

   ```text
Q: LOLIN S2 Mini设备刷写完固件后，系统无法识别出卷标为CIRCUITPT的U盘怎么办？
A: 如果发生了这个问题，那可能就要恭喜你，你中奖了，这个问题可能是我上边说的设备问题，我无法解决。
   只能通过其他方式再次刷写固件，确定自己刷写流程没有问题。
   建议使用https://circuitpython.org/board/lolin_s2_mini/页面提供的TinyUF2的固件刷写方式再次进行刷写，如果还是无法使用，建议联系购买商家处理。
   ```

## switch连接

   ```text
Q: 我把单片机插入到Switch上没有反应怎么办？
A: 需要进行如下检查：
   1、 由于游戏只识别第一个连接的手柄，请在插入单片机前断连自己的无线手柄（switch pro是一个黑色的小圆点，按下断连设备）；
   2、 请查看主机设置，是否启用了USB手柄连接；
   3、 如果仍然无法使用，请在PC使用页面 https://gamepad-tester.com/ 进行测试，看是否能检测到手柄连接，脚本是否正确运行；
   4、 如果上述都没有问题，连接Switch仍无法识别，请更换手柄引擎Switch Pro -> Hori Pad S
   ```

   ```text
Q: 我如何更换手柄引擎？
A: 8.0.0以上版本，直接把 src/root_Hori 目录下所有文件，替换到单片机根目录即可。
   7.3.3版本，需要下载并修改固件源代码，并且把设备信息修改为Hori Pad S的信息
   可以参照 firmware/circuitpython/7.3.3/lolin-s2-mini/hori 目录下方法修改，然后重新编译固件，并重新刷写。更新固件后，再把 src/root_Hori 目录下所有文件，替换到单片机根目录即可。

   ```

## 脚本问题

   ```text
Q: 默认启动脚本是什么？如何修改默认启动脚本？
A: 默认启动脚本为A键连点。修改默认启动脚本方法为：修改 src/resources/config.json 文件的 macros -> autorun 节点。
   具体修改方法参照 run-json.txt 文件。
   ```

   ```text
Q: 如何修改或新建脚本？
A: 请参照 SCRIPTS.md 说明进行操作。
   ```
