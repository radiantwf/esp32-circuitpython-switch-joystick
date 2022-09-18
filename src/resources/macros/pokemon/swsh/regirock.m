--雷吉洛克/雷吉斯奇鲁--
<regirock>
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
	LStick@-128,0:3
	1
	LStick@0,-128:3
	0.5
	LStick@0,-128:0.3
	1
	LStick@-128,0:0.3
	2
	# 踩灯 第3排
	LStick@0,127:1.72
	1
	LStick@127,0:2.5
	2
	# 踩灯 第2排
	LStick@0,-128:0.52
	1
	LStick@-128,0:2.1
	2
	# 踩灯 第1排
	LStick@0,-128:0.52
	1
	LStick@127,0:2.7
	3
	# 等待 并走到石像前
	A:0.1
	1
	LStick@-128,0:0.5
	0.2
	LStick@0,-128:1
	0.2
}