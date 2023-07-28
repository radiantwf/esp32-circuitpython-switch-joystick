--打开宝可梦剑盾--
<open_game--secondary|副设备(副设备启动游戏时校验)|False>
A:0.1
1.5
A:0.1
15
{5}?secondary
A:0.1
1
A:0.1
1
A:0.1
7

--重启宝可梦剑盾--
<restart_game--secondary|副设备(副设备启动游戏时校验)|False>
[common.close_game]
[open_game]


--保存进度--
<save>
X:0.1
1.5
R:0.1
1.5
A:0.1
4

--开启团战 获取瓦特等待（脱机）--
<goto_raid_watts_wait_offline>
A:0.1
0.8
A:0.1
0.8

--开启团战 获取瓦特等待（联机）--
<goto_raid_watts_wait_online>
A:0.1
1
0.8
A:0.1
0.8
2.5


--开启团战（脱机）--
<goto_raid_offline>
[goto_raid_watts_wait_offline]
2.5

--开启团战（联机）--
<goto_raid_online>
[goto_raid_watts_wait_online]
7
2.5


--设置团战密码22223333--
<set_raid_password>
Plus:0.1
1
LStick@127,0
0.5
A:0.1
0.4
A:0.1
0.4
A:0.1
0.4
A:0.1
0.4
LStick@127,0
0.5
A:0.1
0.4
A:0.1
0.4
A:0.1
0.4
A:0.1
0.4
Plus:0.1
1
A:0.1
1


--开启团战并等待其他玩家加入--
<wait_raid>
A:0.1
10
LStick@0,-128:0.1
90


--进行团战--
<raid>
{
	A:0.1
	1
}*20


--联机->脱机--
<offline>
Y:0.1
1
Plus:0.1
0.5
A:0.1
5
B:0.1
0.5
B:0.1
1

--脱机->联机--
<online>
Y:0.1
1
Plus:0.1
30
A:0.1
1
B:0.1
2


--切换网络--
<switch_net>
Y:0.1
1
Plus:0.1
60
A:0.1
1
Plus:0.1
0.5
A:0.1
5
B:0.1
0.5
B:0.1
1.5

--进入时间设置界面--
<set_date_from_home>
# 进入设置界面
LStick@0,127:0.05
0.05
LStick@127,0:0.05
0.05
LStick@127,0:0.05
0.05
LStick@127,0:0.05
0.05
LStick@127,0:0.05
0.05
LStick@127,0:0.05
0.05
A:0.05
1
# 进入时间设置界面
{
	LStick@127,0:0.05
	0.05
}*14
0.05
A:0.05
1
LStick@0,127:0.05
0.05
LStick@0,127:0.05
0.05
LStick@0,127:0.05
0.05
LStick@0,127:0.05
0.05
A:0.05
1
LStick@0,127:0.05
0.05
LStick@0,127:0.05
0.05


--首次修改日期--
<add_one_day_initial>
# 进入设置界面
A:0.05
0.5
# 首次修改日期
A:0.05
0.05
A:0.05
0.05
LStick@0,-128:0.05
0.05
A:0.05
0.05
A:0.05
0.05
A:0.05
0.05
A:0.05
0.12

--后续修改日期--
<add_one_day_initial>
A:0.05
0.12
LStick@-128,0:0.05
0.05
LStick@-128,0:0.05
0.05
LStick@-128,0:0.05
0.05
LStick@0,-128:0.05
0.05
A:0.05
0.05
A:0.05
0.05
A:0.05
0.05
A:0.05
0.12


<battle_check_shiny>
7.8
LStick@0,127:0.1
0.1
LStick@0,127:0.1
2.1
LStick@0,127:0.1
0.5
A:0.1
1.5
A:0.1
0.8
LStick@0,127:0.1
0.3
A:0.1
3.3