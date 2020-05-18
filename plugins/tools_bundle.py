from pikepdf import Pdf, PdfError, PasswordError
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
