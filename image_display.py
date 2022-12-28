import os
from os import path as osp
import gradio as gr
from itertools import chain
from glob import glob
import json
from PIL import Image

item_per_page = 60
images_from_filter = []
images_from_debug = []
image_format = ['jpeg', 'jpg', 'png', 'webp']

def read_aesthetics(image_file):
    file = image_file + "_aesthetic.json"
    if osp.isfile(file):
        with open(file, 'r') as f:
            data = json.load(f)
        return '\n' + '\t'.join([f"{key}: {value:.4f}" for key, value in data.items()])
    return ""
def read_tag(tag_file):
    if osp.isfile(tag_file):
        with open(tag_file, 'r') as f:
            tag = f.read()
    else:
        tag = "Not Found"
    return tag

def handle_page_change(button, index, list_size):
    prev = gr.update(visible=True)
    next = gr.update(visible=True)
    if button == "Previous":
        step = -1
    elif button == "Next":
        step = 1
    else:
        raise gr.Error("Invalid page chnage action")
    
    tmp_index = index + step
    if tmp_index == 0:
        prev = gr.update(visible=False)
    elif tmp_index == list_size - 1:
        next = gr.update(visible=False)
    elif tmp_index < 0 or tmp_index >= list_size:
        raise gr.Error("Invalid Image Index")
    return tmp_index, prev, next

def prepare_data(image_path):
    original_img_path = image_path.replace(
        'debug', 'filter').replace('u_', '')

    img1 = Image.open(original_img_path)
    img2 = Image.open(image_path)

    tag_file = osp.splitext(osp.basename(original_img_path))[0] + '.tag'
    ext = osp.splitext(osp.basename(original_img_path))[1]
    tag_file = original_img_path.replace(ext, '.tag')
    tag = read_tag(tag_file)
    tag += read_aesthetics(image_path.replace('u_', ''))
    
    if 'u_' in image_path:
        tag += "\n Upscaled"
    img_general_info = gr.update(value=f"Tag: {tag}", visible=True)
    original_image_info = gr.update(
        value=f"{img1.width}x{img1.height}", visible=True)
    comppare_image_info = gr.update(
        value=f"{img2.width}x{img2.height}", visible=True)
    return img1, img2, img_general_info, original_image_info, comppare_image_info

def gallery_image_offset(page_index):
    start_id = page_index * item_per_page
    end_id = (page_index + 1) * item_per_page if \
        (page_index + 1) * item_per_page < len(images_from_debug) \
        else None
    return gr.update(value=images_from_debug[start_id:end_id])

def gallery_change_page(page_index, button):
    page_index, prev, next = handle_page_change(button, page_index, len(images_from_debug))
    gallery = gallery_image_offset(page_index)
    return gallery, page_index, prev, next

def load_image_list(file_path, upscale_only, show_all, img_index, page_index):
    global images_from_filter, images_from_debug

    img_index = 0
    page_index = 0
    images = list(chain(
        *[glob(osp.join(file_path, f"**/*.{f}"), recursive=True) for f in image_format]))
    images_from_filter = [i for i in images if 'filter' in i]
    images_from_debug = [i for i in images if 'debug' in i]

    if upscale_only:
        images_from_debug = [i for i in images if 'u_' in i]

    img1, img2, img_general_info, original_image_info, comppare_image_info = prepare_data(
        images_from_debug[img_index])

    image_count = gr.update(visible=True, value=f'''Find {len(images_from_filter)} images in filter folder\n
                         Find {len(images_from_debug)} images in debug folder''')
    if show_all: 
        gallery = gr.update(value= images_from_debug)
        gallery_next = gr.update(visible=False)
    else:
        gallery = gallery_image_offset(page_index)
        gallery_next = gr.update(visible=True)
        
    return image_count, img1, img2, \
        img_general_info, original_image_info, \
        comppare_image_info, img_index, gallery, page_index, gallery_next
        

def change_page(img_index, button):
    img_index, prev, next = handle_page_change(button, img_index, len(images_from_debug))
    image_path = images_from_debug[img_index]

    img1, img2, img_general_info, original_image_info, comppare_image_info = prepare_data(
        image_path)

    return img1, img2, \
        img_general_info, original_image_info, \
        comppare_image_info, img_index, prev, next

GradioTemplateResponseOriginal = gr.routes.templates.TemplateResponse
def reload_javascript():
    with open("image_display.js", "r", encoding="utf8") as jsfile:
        javascript = f'<script>{jsfile.read()}</script>'

    def template_response(*args, **kwargs):
        res = GradioTemplateResponseOriginal(*args, **kwargs)
        res.body = res.body.replace(
            b'</head>', f'{javascript}</head>'.encode("utf8"))
        res.init_headers()
        return res

    gr.routes.templates.TemplateResponse = template_response

if __name__ == '__main__':
    reload_javascript()
    with gr.Blocks(analytics_enabled=False) as demo:
        img_index = gr.State(0)
        page_index = gr.State(0)
        with gr.Row():
            with gr.Column(scale=3):
                folder_dir = gr.Textbox(
                    label="Path to Image Folder", value="/mnt/c/Users/sheldon/Downloads/t/tmp/data")
                file_count = gr.Markdown(
                    visible=False, show_label=False, interactive=False)
                open_btn = gr.Button(value="Open")
            with gr.Column(scale=3):
                upscale_only = gr.Checkbox(label="Only include upscaled image")
                show_all = gr.Checkbox(label="Show all in one page")
            placehodler = gr.Column(scale=6)
        with gr.Tab("Gallery", elem_id="gallery_tab_main"):
            with gr.Row(elem_id= "gallery_main_table"):
                gallery = gr.Gallery(show_label=False).style(
                    grid=[6], height="auto")
            with gr.Row():
                gallery_prev = gr.Button(value="Previous", visible=False)
                gallery_next = gr.Button(value="Next")
        with gr.Tab("Before & After resize"):
            with gr.Row():
                img_general_info = gr.Markdown(visible=False)
            with gr.Row():
                with gr.Column(scale=6):
                    original_image_info = gr.Markdown(visible=False)
                    original_image = gr.Image()
                with gr.Column(scale=6):
                    comppare_image_info = gr.Markdown(visible=False)
                    comppare_image = gr.Image()
            with gr.Row():
                compare_prev = gr.Button(value="Previous", visible=False)
                compare_next = gr.Button(value="Next")

        open_btn.click(fn=load_image_list,
                       inputs=[folder_dir, upscale_only, show_all, img_index, page_index],
                       outputs=[file_count, original_image, comppare_image, img_general_info,
                                original_image_info, comppare_image_info,
                                img_index, gallery, page_index, gallery_next])
        compare_prev.click(fn=change_page,
                   inputs=[img_index, compare_prev],
                   outputs=[original_image, comppare_image, img_general_info,
                            original_image_info, comppare_image_info,
                            img_index, compare_prev, compare_next
                            ],scroll_to_output=True)
        compare_next.click(fn=change_page,
                   inputs=[img_index, compare_next],
                   outputs=[original_image, comppare_image, img_general_info,
                            original_image_info, comppare_image_info,
                            img_index, compare_prev, compare_next
                            ],scroll_to_output=True)
        gallery_prev.click(fn=gallery_change_page,
                inputs=[page_index, gallery_prev],
                outputs=[gallery, page_index, gallery_prev, gallery_next
                        ],scroll_to_output=True)
        gallery_next.click(fn=gallery_change_page,
                inputs=[page_index, gallery_next],
                outputs=[gallery, page_index, gallery_prev, gallery_next
                        ],scroll_to_output=True)
    demo.launch()
