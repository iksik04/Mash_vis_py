from backend.operation import validation
from backend.operation import settings

def main():
    validation.validate()
    #settings.setBinThereshold()
    #settings.setROIcontours()  


if __name__ == "__main__":
    main()