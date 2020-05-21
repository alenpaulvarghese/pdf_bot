from pikepdf import Pdf, PdfError, PasswordError
from plugins.pdfbot_locale import Phrase
from datetime import datetime
import subprocess
import asyncio
import os


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


async def is_encrypted(file_name):
    p1 = subprocess.run(['qpdf', '--is-encrypted', f'{file_name}'])
    if p1.returncode == 0:
        return True
    else:
        return False


async def downloader(chat_id, document_name, client):
    if not os.path.isdir('./FILES'):
        os.mkdir('./FILES')
    location = "./FILES" + "/" + str(chat_id.chat.id)
    if not os.path.isdir(location):
        os.mkdir(location)
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
            return True, 'Worng Password'
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
