from Remotrstage import First_stages
"""""""""
import random

random.seed(10)
def generate_device_id(length):

    letters_and_numbers = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    #asci english character
    device_id = []
    for i in range(length):
        letter = random.choice(letters_and_numbers)
        letter = str(letter)

        device_id.append(letter)
    str_id = "".join(device_id)
    return(str_id)
def generate_device_model():


    model_list= ["yolov5m.pt","yolov5s.pt","yolov5x.pt","yolov5l.pt"]
    return(random.choice(model_list))

def generate_device_FPS ():
    fps_list=[30,31,32,33,34,35,36,37,38,39,40]
    return(random.choice(fps_list))
"""""

def generate_device_parameters(id_len,device_total):
   id_len = 13#int(input("How long would you like the ID to be? "))
   device_total=4#int(input("How many devices do you have? "))
   device_list=[]
   model_type=[]
   #Fps_type=[]
   Edge_fps_value=[]
   for j in range (device_total):
       if j == 0:
           D_id="Shima1"
           model_list = "yolov5m.pt"#before, it was random selection. for fix to have same model i edit to this format
       elif j == 1:
           D_id = "Shima2"
           model_list = "yolov5x.pt"
       elif j==2:
           D_id = "Shima3"
           model_list="yolov5s.pt"
       else:
           D_id = "Shima4"
           model_list="yolov5l.pt"
       device_list.append(D_id)
       model_type.append(model_list)
       #Fps_type.append(generate_device_FPS())
       stage = First_stages(model_type[j], device_list[j])

       Edge_fps_value.append(stage.remote_stages())

   return(model_type, device_list,Edge_fps_value)
          #Edge_fps_value)


