from filter import filter_safe
from filter import filter_ic_im_ih_if_switch
from filter import filter_ic_im_ih_if

def get_filter_list():
    ret = {}
    ret[filter_ic_im_ih_if.filter_name] = filter_ic_im_ih_if.filter
    ret[filter_ic_im_ih_if_switch.filter_name] = filter_ic_im_ih_if_switch.filter
    ret[filter_safe.filter_name] = filter_safe.filter

    return ret