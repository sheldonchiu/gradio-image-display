function gradioApp() {
    const gradioShadowRoot = document.getElementsByTagName('gradio-app')[0].shadowRoot
    return !!gradioShadowRoot ? gradioShadowRoot : document;
}

function get_uiCurrentTab() {
    return gradioApp().querySelector('.tabs button:not(.border-transparent)')
}

function get_uiCurrentTabContent() {
    return gradioApp().querySelector('.tabitem[id^=tab_]:not([style*="display: none"])')
}

function gallery_get_parent_by_class(item, class_name){
    var parent = item.parentElement;
    while(!parent.classList.contains(class_name)){
        parent = parent.parentElement;
    }
    return parent;  
}

function gallery_get_parent_by_tagname(item, tagname){
    var parent = item.parentElement;
    tagname = tagname.toUpperCase()
    while(parent.tagName != tagname){
        parent = parent.parentElement;
    }  
    return parent;
}

var gallery_click_image = function(){
    console.log("in gallery_click_image !")
    console.log(this.classList)
    if (!this.classList.contains("transform")){        
        var gallery = gallery_get_parent_by_class(this, "gallery_container");
        var buttons = gallery.querySelectorAll(".gallery-item");
        var i = 0;
        var hidden_list = [];
        buttons.forEach(function(e){
            if (e.style.display == "none"){
                hidden_list.push(i);
            }
            i += 1;
        })
        if (hidden_list.length > 0){
            setTimeout(images_history_hide_buttons, 10, hidden_list, gallery);
        }        
    }    
    images_history_set_image_info(this); 
}

function gallery_init(){ 
    var tabnames = gradioApp().getElementById("gallery_tab_main")   
    if (tabnames){  
        gradioApp().getElementById('gallery_main_table').classList.add("gallery_container");
    }
    else{
        setTimeout(gallery_init, 500);
    }
}

setTimeout(gallery_init, 500);

document.addEventListener("DOMContentLoaded", function() {
    var mutationObserver = new MutationObserver(function(m){
        var buttons = gradioApp().querySelectorAll('#gallery_main_table .gallery-item');
        buttons.forEach(function(bnt){    
            bnt.addEventListener('click', images_history_click_image, true);
            document.onkeyup = function(e){
                clearTimeout(timer)
                timer = setTimeout(() => {
                    let tab = gradioApp().getElementById("tab_images_history").getElementsByClassName("bg-white px-4 pb-2 pt-1.5 rounded-t-lg border-gray-200 -mb-[2px] border-2 border-b-0")[0].innerText
                    bnt = gradioApp().getElementById(tab+"_images_history_gallery").getElementsByClassName('gallery-item !flex-none !h-9 !w-9 transition-all duration-75 !ring-2 !ring-orange-500 hover:!ring-orange-500 svelte-1g9btlg')[0]
                    images_history_click_image.call(bnt)
                },500)
                
            }
        });

        var cls_btn = gradioApp().getElementById(tabname + '_images_history_gallery').querySelector("svg");
        if (cls_btn){
            cls_btn.addEventListener('click', function(){
                gradioApp().getElementById(tabname + '_images_history_renew_page').click();
            }, false);
        }

 
    });
    mutationObserver.observe(gradioApp(), { childList:true, subtree:true });
});