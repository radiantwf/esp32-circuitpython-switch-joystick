--雷吉洛克/雷吉斯奇鲁--
<regirock|雷吉洛克/雷吉斯奇鲁（定点）|999999--secondary|副设备(副设备启动游戏时校验)|False>
{
	[common.wakeup_joystick]
	[pokemon.swsh.common.restart_game]
	body:
	A:0.1
	1
	A:0.1
	1.2
	A:0.1
	6.5
	[pokemon.swsh.common.battle_check_shiny]
	A:0.1
	0.5
	# 走到左上角墙角
	LStick@-127,0:1.8
	LStick@9,0:0.05
	0.3
	LStick@0,-127:0.7
	LStick@0,9:0.05
	0.2
	LStick@0,-127:0.3
	LStick@9,0:0.05
	0.3
	LStick@-127,0:0.3
	LStick@9,0:0.05
	0.7
	# 踩灯 第3排
	LStick@0,127:1.74
	LStick@0,-9:0.05
	0.3
	LStick@127,0:2.5
	LStick@-9,0:0.05
	0.7
	# 踩灯 第2排
	LStick@0,-127:0.52
	LStick@0,9:0.05
	0.3
	LStick@-127,0:2.1
	LStick@9,0:0.05
	0.7
	# 踩灯 第1排
	LStick@0,-127:0.52
	LStick@0,9:0.05
	0.3
	LStick@127,0:2.7
	3
	# 等待 并走到石像前
	A:0.1
	1
	LStick@-127,0:0.5
	0.2
	LStick@0,-127:1
	0.2
}
