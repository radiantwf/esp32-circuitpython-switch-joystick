--雷吉艾勒奇--
<regieleki|雷吉艾勒奇（定点）|999999--secondary|副设备(副设备启动游戏时校验)|False>
{
	[pokemon.swsh.common.restart_game]
	body:
	A:0.1
	1
	A:0.1
	1.2
	A:0.1
	6.65
	[pokemon.swsh.common.battle_check_shiny]
	A:0.1
	0.5
	# 踩灯
	LStick@-127,0:1.8->LStick@9,0:0.05->0.3->LStick@0,-127:0.8->LStick@0,9:0.05->0.2->LStick@0,-127:0.3->LStick@9,0:0.05->0.3->LStick@-127,0:0.3->LStick@9,0:0.05->0.7->LStick@0,127:1.64->LStick@0,-9:0.05->0.3->LStick@127,0:2.5->LStick@-9,0:0.05->0.7->LStick@0,-127:0.44->LStick@0,9:0.05->0.3->LStick@-127,0:2.1->LStick@9,0:0.05->0.7->LStick@0,-127:0.42->LStick@0,9:0.05->0.3->LStick@127,0:2.7
	3
	# 等待 并走到石像前
	A:0.1
	1
	LStick@0,-127:1
	0.2
	LStick@-127,0:0.54
	0.2
	LStick@0,-127:0.1
	0.2
}

--雷吉洛克/雷吉斯奇鲁--
<regirock|雷吉洛克/雷吉斯奇鲁（定点）|999999--secondary|副设备(副设备启动游戏时校验)|False>
{
	[pokemon.swsh.common.restart_game]
	body:
	A:0.1
	1
	A:0.1
	1.2
	A:0.1
	7
	[pokemon.swsh.common.battle_check_shiny]
	A:0.1
	0.5
	# 走到左上角墙角
	{
		LStick@-80,-100:0.4->B|LStick@-80,-100:0.1->~
	} * 9
	0.7
	# 踩灯 第3排
	LStick@0,127:1.79->LStick@0,-9:0.05
	0.3
	LStick@127,0:2.5->LStick@-9,0:0.05
	0.7
	# 踩灯 第2排
	LStick@0,-127:0.535->LStick@0,9:0.05
	0.3
	LStick@-127,0:2.1->LStick@9,0:0.05
	0.7
	# 踩灯 第1排
	LStick@0,-127:0.53->LStick@0,9:0.05
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