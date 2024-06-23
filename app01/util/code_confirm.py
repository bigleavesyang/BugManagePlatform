from PIL import Image, ImageDraw, ImageFont
import random


# 生成背景图片
def generate_background(width, height, color=(255, 255, 255)):
    background = Image.new('RGB', (width, height), color=color)
    return background


# 生成滑块缺口
def generate_gap(background, gap_size, position):
    draw = ImageDraw.Draw(background)
    gap_start = position
    gap_end = position + gap_size
    draw.rectangle([gap_start, 0, gap_end, background.height], fill=(0, 0, 0))
    return background


# 生成滑块图片
def generate_slider(width, height, color=(255, 0, 0)):
    slider = Image.new('RGB', (width, height), color=color)
    return slider


# 将滑块图片放置在背景图片上
def place_slider(background, slider, gap_position, slider_position):
    background.paste(slider, (gap_position - slider.width // 2 + slider_position, 0))
    return background


# 设置字体和文本
def set_text(draw, text, position, font, fill=(0, 0, 0)):
    text_width, text_height = draw.textsize(text, font=font)
    draw.text((position[0] - text_width // 2, position[1] - text_height // 2), text, fill=fill, font=font)


# 主函数，生成最终的滑块验证码图片
def generate_slider_captcha(background_width, background_height, gap_size, slider_width, slider_height):
    # 初始化
    background = generate_background(background_width, background_height)
    gap_position = random.randint(10, background_width - gap_size - 10)  # 随机生成缺口位置
    slider_position = random.randint(0, background_width - gap_position - slider_width)  # 随机生成滑块初始位置
    slider = generate_slider(slider_width, slider_height)

    # 字体设置
    # font = ImageFont.truetype('arial.ttf', 16)  # 假设你有一个arial.ttf字体文件
    text = '拖动滑块验证'

    # 绘制滑块缺口
    background = generate_gap(background, gap_size, gap_position)

    # 绘制文本
    draw = ImageDraw.Draw(background)
    set_text(draw, text, (background_width // 2, background_height - 20), font=None)

    # 放置滑块
    background = place_slider(background, slider, gap_position, slider_position)

    # 保存到文件
    background.save('slider_captcha.png')


# 调用主函数生成图片
generate_slider_captcha(600, 200, 50, 50, 50)