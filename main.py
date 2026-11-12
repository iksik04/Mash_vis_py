from backend.operation import validation
from backend.operation import settings
from backend.operation import process

def main():
    frame = process.grab_frame()
    validation.validate(frame)
    #settings.setContourLenghtBinThereshold()
    #settings.setRefContext()
    #settings.setROIcontours()  


if __name__ == "__main__":
    main()