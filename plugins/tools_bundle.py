from pikepdf import Pdf, PdfError, PasswordError
from pylovepdf.tools.compress import Compress
from pyrogram import InputMediaPhoto
from plugins.pdfbot_locale import Phrase
from datetime import datetime, date
import subprocess
import os
import asyncio

async def pdf_silcer(location, message_id, client, msg, naming):
    try:
        with Pdf.open(location, 'wb') as pdf:
            file_name = location.split('/')[-1]
            file_name = os.path.splitext(file_name)[0]
            current_directory = os.getcwd()
            os.chdir(f'./FILES/{message_id}/')
            for n, page in enumerate(pdf.pages):
                await msg.edit(text=f'Uploading {int(n)+1} of {len(pdf.pages)}')
                dst = Pdf.new()
                dst.pages.append(page)
                location = (f'{str(file_name)}-{naming}-{n}.pdf')
                dst.save(location)
                await client.send_document(
                    document=location,
                    chat_id=message_id
                )
                os.remove(location)
            os.chdir(current_directory)
            await msg.reply(text=f'Successfully Uploaded {int(n)+1} files')
    except PasswordError as e:
        await msg.edit('Please decrypt the PDF')
        await asyncio.sleep(10)


async def page_no(input):
    try:
        with Pdf.open(input, 'wb') as pdf:
            return len(pdf.pages)
    except PasswordError:
        return "Soory the file is encrypted"
    except PdfError:
        return "The File is corrupted"


async def is_encrypted(file_name):
    p1 = subprocess.run(['qpdf', '--is-encrypted', f'{file_name}'])
    if p1.returncode == 0:
        return True
    else:
        return False


async def downloader(chat_id, document_name, client):
    if not os.path.isdir('./FILES'):
        os.mkdir('./FILES')
    location = f"./FILES/{str(chat_id.chat.id)}/{str(chat_id.message_id)}"
    if not os.path.isdir(location):
        os.makedirs(location)
    pdfdir = location + "/" + document_name
    await client.download_media(
        message=chat_id,
        file_name=pdfdir
    )
    return pdfdir, location


async def encrypter(file_name, password, location, id_for_naming):
    if not await is_encrypted(file_name):
        print(file_name)
        final_name = os.path.splitext(file_name)[0]
        final_name = f'{final_name}-{id_for_naming}-encrypted.pdf'
        p1 = subprocess.run(['qpdf',
                            '--encrypt',
                             f'{password}', f'{password}',
                             '128', '--',
                             f'{file_name}', f'{final_name}'],
                            )
        os.remove(file_name)
        if p1.returncode == 0:
            return False, final_name
        elif p1.returncode == 2:
            return True, Phrase.MAIN_CORRUPT
        else:
            return True, Phrase.WENT_WRONG
    else:
        os.remove(file_name)
        return True, "The Given file is already encrypted"


async def decrypter(file_name, password, location, id_for_naming):
    if await is_encrypted(file_name):
        final_name = os.path.splitext(file_name)[0]
        final_name = f'{final_name}-{id_for_naming}-decrypted.pdf'
        p1 = subprocess.run(['qpdf', f'--password={password}', '--decrypt',
                            f'{file_name}', final_name])
        os.remove(file_name)
        if p1.returncode != 0:
            return True, 'Wrong Password'
        else:
            return False, final_name
    else:
        os.remove(file_name)
        return True, 'The file has no protection'


async def merger(file_name, id_for_naming, location):
    merged_pdf = Pdf.new()
    for file in file_name:
        try:
            with Pdf.open(file, 'rb') as src:
                merged_pdf.pages.extend(src.pages)
        except PasswordError as e:
            return False, Phrase.INVALID_PASSWORD.format(issue_with=file.split("/")[-1])
        except Exception as e:
            with open("error_logging.txt", "at") as err_logger:
                err_logger.write(Phrase.MERGE_ERR_LOG.format(
                    time=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    issue=e
                ))
            return False, Phrase.MERGE_CORRUPT.format(issue_with=file.split("/")[-1])
    merged_pdf.remove_unreferenced_resources()
    merge_file_location = os.path.join(location, f'merged-{id_for_naming}.pdf')
    merged_pdf.save(merge_file_location)
    return True, merge_file_location


async def compressor(compression_ratio, location, file_name):
    try:
        #os.environ.get(COMPRESS_API)
        API_PDF = 'project_public_b5530332283b096e921c0e6e8df8a12a_1HzdL6b2fc4ee89ae7031bb53977e325c2df3'
    except Exception:
        print('API FOR COMPRESSION NOT FOUND')
        return False, 'compression is unavailable currently'
    try:
        t = Compress(API_PDF, verify_ssl=True, proxies=False)
        t.add_file(file_name)
        t.debug = False
        t.compression_level = compression_ratio
        t.set_output_folder(location)
        t.execute()
        t.download()
        t.delete_current_task()
        tday = date.today().strftime("%d-%m-%Y")
        return True, f'{location}/compress_{tday}.pdf'
        await client.send_document(
            document=f'{location}/compress_{tday}.pdf',
            chat_id=callback_query.message.chat.id,
            caption="Compressed PDF"
        )
    except Exception as e:
        with open("error_logging.txt", "at") as err_logger:
                err_logger.write(Phrase.MERGE_ERR_LOG.format(
                    time=datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                    issue=e
                ))
        return False, 'Error occured while compressing'


async def get_image_page(pdf_file, out_file, message_id, page_num):
    total_pages = await page_no(pdf_file)
    if type(total_pages) != int:
        return False, total_pages
    print(total_pages)
    if type(page_num) == int:
        if page_num > total_pages:
            return False, Phrase.PAGES_HIGH
        else:
            command_to_exec = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=jpeg", "-r510x510", "-dPDFFitPage"]
            extracted_file_location = out_file+'/extracted'+str(message_id)+'.jpeg'
            command_to_exec.append("-sOutputFile=" + extracted_file_location)
            command_to_exec.append("-dFirstPage=" + str(page_num))
            command_to_exec.append("-dLastPage=" + str(page_num))
            command_to_exec.append(pdf_file)
            process = await asyncio.create_subprocess_exec(
                *command_to_exec)
            return True, extracted_file_location

    elif type(page_num) == list:
        start_page = page_num[0]
        end_page = page_num[1]
        list_to_upload = []
        if start_page <= total_pages and end_page >= start_page and end_page <= total_pages:
            for i in range(start_page, end_page+1):
                print(i)
                command_to_exec = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=jpeg", "-r510x510", "-dPDFFitPage"]
                extracted_file_location = out_file+'/extracted-'+str(message_id)+'-'+str(i)+'.jpeg'
                command_to_exec.append("-sOutputFile=" + extracted_file_location)
                command_to_exec.append("-dFirstPage=" + str(i))
                command_to_exec.append("-dLastPage=" + str(i))
                command_to_exec.append(pdf_file)
                print(command_to_exec)
                process = await asyncio.create_subprocess_exec(
                    *command_to_exec)
                await process.communicate()
                list_to_upload.append(InputMediaPhoto(extracted_file_location))
            await asyncio.sleep(2)
            return True, list_to_upload
        else:
            return False, 'out of range'

    elif page_num is None:
        list_to_upload = []
        for page in range(total_pages):
            command_to_exec = ["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=jpeg", "-r510x510", "-dPDFFitPage"]
            extracted_file_location = out_file+'/extracted'+str(message_id)+'-'+str(page+1)+'.jpeg'
            command_to_exec.append("-sOutputFile=" + extracted_file_location)
            command_to_exec.append("-dFirstPage=" + str(page+1))
            command_to_exec.append("-dLastPage=" + str(page+1))
            command_to_exec.append(pdf_file)
            process = await asyncio.create_subprocess_exec(
                *command_to_exec)
            await process.communicate()
            list_to_upload.append(InputMediaPhoto(extracted_file_location))

        await asyncio.sleep(2)
        return True, list_to_upload
