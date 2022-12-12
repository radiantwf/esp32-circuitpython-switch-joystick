--朱紫孵蛋--
<hatch_eggs|朱紫孵蛋|1--start_col|起始列(0-5)|0--last_col|终止列(0-5)|5--last_page|终止页面(0为当前页面)|0--cycles|孵化周期|20--flame_body|火焰身躯(默认为True)|True>
body:
EXEC>last_page=int(last_page);last_col=int(last_col);start_col=int(start_col);flame_body=flame_body.lower()=='true'
EXEC>current_page=0;current_col=start_col;
EXEC>loop_times=last_page*6+last_col-start_col+1
EXEC>cycles=int(cycles)*2
{
	EXEC>cycles=int(cycles)*2
}?not|space|flame_body

# 打开盒子
X:0.05
0.8
A:0.05
3
{
	# 判断是否需要翻页
	{
		R:0.05
		0.5
		EXEC>current_col=0
		EXEC>current_page=current_page+1
	}?current_col>5
	# 选择列
	{
		LStick@127,0:0.05
		0.2
	}*current_col
	0.4
	MINUS:0.01->0.008->MINUS:0.05
	0.8
	{
		LStick@0,127:0.05
		0.2
	}*4
	0.6
	A:0.01->0.008->A:0.05
	0.5
	{
		LStick@-127,0:0.05
		0.2
	}*(current_col+1)
	LStick@0,127:0.05
	0.8
	A:0.01->0.008->A:0.05
	0.8
	# 关闭盒子
	{
		B:0.05
		0.05
	}*15
	0.8

	L:0.05
	0.6
	{
		LStick@-0,-127|RStick@-127,0:0.5->LStick@-0,-127|RStick@-127,0|LPRESS:0.1->LStick@-0,-127|RStick@-127,0:5.4->~
	}*int((cycles+4)/5)
	1
	{
		A:0.1
		0.1
	}*90
	4
	{
		L:0.05
		0.6
		LPRESS:0.01
		LPRESS:0.01
		{
			LStick@-0,-127|RStick@-127,0:0.5->LStick@-0,-127|RStick@-127,0|LPRESS:0.1->LStick@-0,-127|RStick@-127,0:12->~
		}flame_body
		{
			LStick@-0,-127|RStick@-127,0:0.5->LStick@-0,-127|RStick@-127,0|LPRESS:0.1->LStick@-0,-127|RStick@-127,0:20->~
		}?not|space|flame_body
		1
		{
			A:0.1
			0.1
		}*90
		4
	}*4

	# 打开盒子
	X:0.05
	0.8
	A:0.05
	3
	LStick@-127,0:0.05
	0.2
	LStick@0,127:0.05
	0.6
	MINUS:0.01->0.008->MINUS:0.05
	0.8
	{
		LStick@0,127:0.05
		0.2
	}*4
	0.6
	A:0.01->0.008->A:0.05
	0.8
	LStick@0,-127:0.05
	0.2
	{
		LStick@127,0:0.05
		0.2
	}*current_col+1
	0.6
	A:0.01->0.008->A:0.05
	0.8
	{
		LStick@-127,0:0.05
		0.2
	}*current_col
	EXEC>current_col=current_col+1
}*loop_times

# 关闭盒子
{
	B:0.05
	0.05
}*15
0.7




--朱紫野餐取蛋--
<get_eggs|朱紫野餐|1--get_eggs_times|取蛋次数（每次等待2分钟）|15>
[pokemon.scarletviolet.common.restart_game]
X:0.1
0.8
LStick@127,0:0.05
0.1
LStick@0,127:0.05
0.1
LStick@0,127:0.035
0.1
body:
A:0.1
0.1
9
# 往前走一步，开始做料理
LStick@0,-127:0.2
0.8
A:0.1
0.5
A:0.1
5
# 选择超级花生酱三明治（配方：香蕉，花生酱，黄油 各1）
{
	LStick@0,127:0.05
	0.3
}*8
A:0.1
0.7
A:0.1
7
{
	LStick@0,-127:0.5
	0.1
	A:0.1->LStick@0,127|A:0.48->A:0.5
	0.1
}*3
0.6
A:0.1
2
A:0.1
3.5
A:0.1
12
A:0.1
9
A:0.1
0.5
15
A:0.1
2
LStick@127,0:0.4->LStick@0,-127:0.4->LStick@-127,0:0.16
{
	# 单次循环周期120s
	106
	{
		A:0.025
		0.1
	}*100
	{
		B:0.05
		0.2
	}*4
	0.5
}*int(get_eggs_times)
1
{
	Y:0.05
	0.5
}*3
A:0.05
0.5
A:0.05
2.5
{
	A:0.05
	0.1
}*10
L:0.05
1
X:0.1
0.8



--朱紫放生--
<release_pokemons|朱紫放生|1--start_col|起始列(0-5)|0--last_col|终止列(0-5)|5--last_page|终止页面(0为当前页面)|0>
body:
EXEC>current_page=0;current_col=int(start_col);
EXEC>loop_times=int(last_page)*6+int(last_col)-int(start_col)+1

# 打开盒子
X:0.05
0.8
A:0.05
3
# 选择列
{
	LStick@127,0:0.05
	0.2
}*current_col
{
	# 判断是否需要翻页
	{
		R:0.05
		0.7
		LStick@127,0:0.05
		0.2
		EXEC>current_col=0
		EXEC>current_page=current_page+1
	}?current_col>5
	0.4
	[release_a_pokemon]
	{
		LStick@0,127:0.05
		0.4
		[release_a_pokemon]
	}*4
	{
		LStick@0,127:0.05
		0.2
	}*3
	LStick@127,0:0.05
	0.4
	EXEC>current_col=current_col+1
}*loop_times

# 关闭盒子
{
	B:0.05
	0.05
}*15
0.7



--放生1只精灵--
<release_a_pokemon>
A:0.01->0.008->A:0.05
0.6
TOP:0.01->0.008->TOP:0.05
0.1
TOP:0.01->0.008->TOP:0.05
0.1
A:0.01->0.008->A:0.05
0.6
TOP:0.01->0.008->TOP:0.05
0.1
A:0.01->0.008->A:0.05
1.6
A:0.01->0.008->A:0.05
0.6