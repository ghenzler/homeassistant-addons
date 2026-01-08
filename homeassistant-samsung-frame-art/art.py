import sys
import os
import asyncio
import logging
import argparse
import shutil
from PIL import Image, ImageOps


sys.path.append('../')

from samsungtvws.async_art import SamsungTVAsyncArt
from samsungtvws import exceptions



logging.basicConfig(level=logging.INFO) #or logging.DEBUG to see messages

def parseargs():
    # Add command line argument parsing
    parser = argparse.ArgumentParser(description='Example async art Samsung Frame TV.')
    parser.add_argument('--ip', action="store", type=str, default=None, help='ip address of TV (default: %(default)s))')
    parser.add_argument('--filter', action="store", type=str, default="none", help='photo filter to apply (default: %(default)s))')
    parser.add_argument('--matte', action="store", type=str, default="none", help='matte to apply (default: %(default)s))')
    parser.add_argument('--matte-color', action="store", type=str, default="black", help='matte color to apply (default: %(default)s))')
    return parser.parse_args()
    

# Set the path to the folder containing the images
folder_path = '/media/frame'
uploaded_folder_path = '/media/frame-uploaded'


async def main():
    args = parseargs()

    matte = args.matte
    matte_color = args.matte_color

    # Set the matte and matte color

    if matte != 'none':
        matte_var = f"{matte}_{matte_color}"
    else:
        matte_var = matte



    tv = SamsungTVAsyncArt(host=args.ip, port=8002)
    await tv.start_listening()
    
    supported = await tv.supported()
    if supported:
        logging.info('This TV is supported')

    else:
        logging.info('This TV is not supported')
   
    if supported:
        try:
            #is tv on (calls tv rest api)
            tv_on = await tv.on()
            logging.info('tv is on: {}'.format(tv_on))
            
            #is art mode on
            #art_mode = await tv.get_artmode()                  #calls websocket command to determine status
            art_mode = tv.art_mode                              #passive, listens for websocket messgages to determine art mode status
            logging.info('art mode is on: {}'.format(art_mode))

            #get current artwork
            info = await tv.get_current()
            # logging.info('current artwork: {}'.format(info))

            # Check if folder exists before listing
            if not os.path.exists(folder_path):
                logging.error('Folder {} does not exist'.format(folder_path))
                return
            
            photos = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not photos:
                logging.info('No PNG or JPG photos found in the folder')
                return
            
            for photo in photos:
                try:
                    filename = os.path.join(folder_path, photo)
                    # Skip if file doesn't exist (might have been moved already)
                    if not os.path.exists(filename):
                        continue
                    
                    # Rename to lowercase
                    new_filename = os.path.join(folder_path, os.path.basename(filename).lower())
                    if filename != new_filename:
                        os.rename(filename, new_filename)
                        filename = new_filename
                    logging.info('Processing photo: {}'.format(filename))

                    # Open and process image
                    image = Image.open(filename)
                    image = ImageOps.exif_transpose(image)
                    new_image = image.resize((3840, 2160))
                    new_image.save(filename)

                    # Upload to TV
                    with open(filename, "rb") as f:
                        file_data = f.read()
                    file_type = os.path.splitext(filename)[1][1:] 
                    content_id = await tv.upload(file_data, file_type=file_type, matte=matte_var) 
                    logging.info('uploaded {} to tv as {}'.format(filename, content_id))
                    await tv.set_photo_filter(content_id, args.filter)

                    await tv.select_image(content_id, show=False)
                    logging.info('set artwork to {}'.format(content_id))
                    
                    # Move uploaded image to uploaded folder
                    uploaded_filename = os.path.join(uploaded_folder_path, os.path.basename(filename))
                    shutil.move(filename, uploaded_filename)
                    logging.info('moved {} to {}'.format(filename, uploaded_filename))
                    
                except Exception as e:
                    logging.warning('Error processing photo {}: {}'.format(photo, e))
                    continue

               
            await asyncio.sleep(15)

        except exceptions.ResponseError as e:
            logging.warning('ERROR: {}'.format(e))
        except AssertionError as e:
            logging.warning('no data received: {}'.format(e))

        
    await tv.close()


asyncio.run(main())