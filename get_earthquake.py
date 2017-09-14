import urllib2
import re
import sys
import math

from PIL import Image,ImageDraw,ImageFont,ImageOps
im = Image.open('bmng.jpg')
img_w = im.size[0]/2;   # Get the width of the image
img_h = im.size[1]/2;   # Get the height of the image
img_a = img_w /180;
lin_with = 4;           # Draw the line width of the cross
lin_long = 10;          #Cross the line length

dl = 25;        # Draw the length of the line
angl = 70;      #Draw the tilt angle of the line
offset_x = dl*  math.cos( math.radians(angl));      #The offset of the line X coordinate
offset_y = dl*  math.sin( math.radians(angl));      #The offset of the Y coordinate of the line

type = sys.getfilesystemencoding()

url = 'http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.atom'

print url
# read url
content = urllib2.urlopen(url).read()
# 
content = content.decode("UTF-8").encode(type)
#The format of the web content
#</id><title>M 2.7 - 22km NW of Nikiski, Alaska</title><updated>2016-11-24T02:57:07.027Z</updated><link rel="alternate" type="text/html" href="http://earthquake.usgs.gov/earthquakes/eventpage/ak14401253"/><summary type="html"><![CDATA[<dl><dt>Time</dt><dd>2016-11-24 02:33:16 UTC</dd><dd>2016-11-23 17:33:16 -09:00 at epicenter</dd><dt>Location</dt><dd>60.854&deg;N 151.518&deg;W</dd><dt>Depth</dt><dd>72.70 km (45.17 mi)</dd></dl>]]></summary><georss:point>60.8539 -151.5176</georss:point><georss:elev>-72700</georss:elev><category label="Age" term="Past Day"/><category label="Magnitude" term="Magnitude 2"/><category label="Contributor" term="ak"/><category label="Author" term="ak"/></entry>
#nation = re.findall(r'</id><title>M (.*) - (.*) of (.*), (.*)</title><updated>', content)

#Get the name of the earthquake location
nation = re.findall(r'</id><title>M (.*) - (.*?)</title><updated>', content)
#Obtain the time of occurrence of the earthquake site
utc_time = re.findall(r'Time</dt><dd>(.*?) (.*?) UTC</dd><dd>', content)
#Get the geography latitude and longitude coordinates of the earthquake site
location = re.findall(r'</dd><dt>Location</dt><dd>(.*)&deg;(.*) (.*)&deg;(.*)</dd><dt>', content)


def lngToPx(num,lng):   #Longitude values are converted to X coordinates on the map
    if lng=='E':
        #num = 2700 +  (num*15);
        num = img_w +  (num*img_a);
    elif lng=='W':        
        #num = 2700 -  (num*15);
        num = img_w -  (num*img_a);
    else:
        return -1;        
    return num;

def latToPy(num,lat):   #The dimension value is converted to the Y coordinate on the map  
    if   lat == 'N':
        #num = 1350*(1 - (num/90));
        num = img_h*(1 - (num/90));
    elif lat == 'S':
        #num = 1350*(1 + (num/90));
        num = img_h*(1 + (num/90));
    else :
        return -1;
    return num;
    


#Apply a two-dimensional array to store the processed data
coord_num = [[0 for col in range(5)] for row in range(len(nation))] 

#Processes the coordinate information obtained from the web page, converted to coordinates that can be drawn directly on the map
def coordinate_process():    
    for loop_c in range(0,len(nation),1):        
        text_pixe = len(nation[loop_c][1])*6; #地理名称占用的像素点长度

        #The page gets the longitude value converted to the X coordinate
        coord_num[loop_c][0] = int(lngToPx(float(location[loop_c][2]),location[loop_c][3]));
        #The dimension value obtained by the page is converted to the Y coordinate
        coord_num[loop_c][1] = int(latToPy(float(location[loop_c][0]),location[loop_c][1]));

        if (coord_num[loop_c][0] > 5100):   #Avoid mapping geographic names to string overrides
            coord_num[loop_c][2] = coord_num[loop_c][0] - offset_x;
            if (coord_num[loop_c][1] > offset_y):
                coord_num[loop_c][3] = coord_num[loop_c][1] - offset_y;
        else:
            coord_num[loop_c][2] = coord_num[loop_c][0] + offset_x;
            if (coord_num[loop_c][1] > offset_y):
                coord_num[loop_c][3] = coord_num[loop_c][1] - offset_y;

         #Processing the geographical name string up and down the interval, to avoid the subsequent drawing of the string over the previously drawn string
        for compl in range(0,loop_c,1):
            #If the interval between the two strings is coincident with the X interval
            if ((abs(coord_num[loop_c][3] - coord_num[compl][3]) < 25 ) and (abs(coord_num[loop_c][2] - coord_num[compl][2]) < text_pixe+5)):
                if (coord_num[loop_c][3] < img_h*2 - 25):
                    coord_num[loop_c][3] = coord_num[compl][3] + 25;    #There is a coincidence to increase the interval between the two

        if (coord_num[loop_c][0] > 5100):   #Avoid mapping geographic names to string overrides
            coord_num[loop_c][4] = coord_num[loop_c][2] - text_pixe - 5;
        else:
            coord_num[loop_c][4] = coord_num[loop_c][2] + text_pixe + 5;

#Draw the cross mark and the earthquake location marker line on the earthquakes on the map image
def draw_cross():
    draw = ImageDraw.Draw(im) 
    for loop in range(0,len(nation),1):
        print "   Nation  : "+nation[loop][1]
       # print "   Area    : "+nation[loop][2]
        print " Magnitude : "+nation[loop][0]
        print "Origin Time: "+utc_time[loop][0]+" "+utc_time[loop][1]+" UTC"
        print " Location  : "+location[loop][0]+location[loop][1]+" "+location[loop][2]+location[loop][3]
        print ("X: ",coord_num[loop][0])
        print ("Y: ",coord_num[loop][1])

        R = 255;
        G = (loop*8)%256;
        B = ((loop%10)*27)%256;

        #Draw a cross mark on the earthquakes on the map image
        draw.line((coord_num[loop][0]-lin_long,coord_num[loop][1]-lin_long,coord_num[loop][0]+lin_long,coord_num[loop][1]+lin_long), (R,G,B),width = lin_with)
        draw.line((coord_num[loop][0]-lin_long,coord_num[loop][1]+lin_long,coord_num[loop][0]+lin_long,coord_num[loop][1]-lin_long), (R,G,B),width = lin_with)

        #Draw a marker line at an earthquake location on a map image
        draw.line((coord_num[loop][0],coord_num[loop][1],coord_num[loop][2],coord_num[loop][3]), (R,G,B),width = 1);
        draw.line((coord_num[loop][2],coord_num[loop][3],coord_num[loop][4],coord_num[loop][3]), (R,G,B),width = 1)


        if loop == (len(nation)-1):
            im.save("out.jpg")
            del draw

        print "--------------------------------------"

#Mapping the geographic information and the time of the earthquake in the vicinity of the marked line of the earthquake site
def draw_text():
    out = Image.open('out.jpg');
    draw_out = ImageDraw.Draw(out);

    for loop_text in range(0,len(nation),1):
        #Change UTC time to UTC + 8 time
        utc8 = str((int(utc_time[loop_text][1][0:2])+8)%24);
        if len(utc8) == 1:
            utc8 = '0'+ utc8;
        utc8 = utc8+utc_time[loop_text][1][2:];
        
        if (coord_num[loop_text][0] > 5100):    #Avoid mapping geographic names to string overrides            
            draw_out.text([coord_num[loop_text][4],coord_num[loop_text][3]],nation[loop_text][0]+"M "+utc_time[loop_text][0]+" "+utc8+" UTC+8",(0,255,255))
            draw_out.text([coord_num[loop_text][4],coord_num[loop_text][3]-10],nation[loop_text][1],(128,255,0))

        else:   #Draw a geographic name string
            draw_out.text([coord_num[loop_text][2]+5,coord_num[loop_text][3]],nation[loop_text][0]+"M "+utc_time[loop_text][0]+" "+utc8+" UTC+8" ,(0,255,255))
            draw_out.text([coord_num[loop_text][2]+5,coord_num[loop_text][3]-10],nation[loop_text][1],(128,255,0))

    if loop_text == (len(nation)-1):
        out.save("out.jpg")
        del draw_out 
    
        

coordinate_process();
draw_cross();
draw_text();

print "----Done----"

