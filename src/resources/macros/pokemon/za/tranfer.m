--原地传送--
<tranfer|ZA - 原地传送(默认参数为5区传送覆盖5区、16区)|-1--x_offset|地区传送-摇杆横向位移参数(左-127~127右)|20--y_offset|地区传送-摇杆纵向位移参数(上-127~127下)|-80--delay|地图传送-摇杆移动持续时间|0.06>
Plus:0.1
0.3
LStick@-*x_offset*-,-*y_offset*-:-*delay*-
0.1
A:0.1
0.5
A:0.1
A:0.1
3

--18区刷暴飞龙（走到门口）--
<tranfer_Area18|ZA - 18区刷暴飞龙（走到门口）|-1>
LStick@0,-127:0.03->LStick@0,-127|B:0.02->LStick@0,-127:1
0.3
Plus:0.1
0.3
LStick@-64,64:0.1
0.1
A:0.1
0.5
A:0.1
A:0.1
3

--20区 左侧大范围覆盖--
<tranfer_area20_left|ZA - 20区左侧大范围覆盖|-1>
EXEC>enter_pokemonCenter_x_offset=-60;enter_pokemonCenter_y_offset=-127;enter_pokemonCenter_delay=0.25
EXEC>leave_pokemonCenter_x_offset=-30;leave_pokemonCenter_y_offset=127;leave_pokemonCenter_delay=0.2
EXEC>wholeDay_flag=False
EXEC>cycles=33
body:
EXEC>index=0
[pokecenter_bench]
{
    EXEC>index=index+1
    LStick@0,-127:0.03->LStick@0,-127|B:0.02->LStick@0,-127:1
    0.3
    A:0.1
    2.5
    LStick@-75,-127:0.03->LStick@-75,-127|B:0.02->LStick@-75,-127:5->~
    LStick@75,127:5.5->A:0.1
    3
    EXEC>flag=index<cycles
    {
        Plus:0.1
        Plus:0.1
        0.3
        LStick@-127,-20:0.1
        0.1
        [do_transfer]
    }?flag
}*cycles

--传送--
<do_transfer>
A:0.1
0.5
A:0.1
A:0.1
3

--宝可梦中心 长椅休息--
<pokecenter_bench>
Plus:0.1
0.3
LStick@-*enter_pokemonCenter_x_offset*-,-*enter_pokemonCenter_y_offset*-:-*enter_pokemonCenter_delay*-
0.1
[do_transfer]
LStick@127,-50:0.03->LStick@127,-50|B:0.02->LStick@127,-50:1.8->~
LStick@30,-127:1.6
{
    A:0.05->0.05->~
}*10*3
15
{
    {
        LStick@0,127|A:0.05->LStick@0,127:0.05->~
    }*10*3
    15
}?wholeDay_flag
Plus:0.1
0.3
LStick@-*leave_pokemonCenter_x_offset*-,-*leave_pokemonCenter_y_offset*-:-*leave_pokemonCenter_delay*-
0.1
[do_transfer]
2
