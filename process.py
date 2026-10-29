
import roi

def ref_init(img, trackers, save2file = False):


    tr = roi.init_reference(img, name=f"roi_{len(trackers)}")
    if tr is not None:
        trackers.add(tr)

    return trackers