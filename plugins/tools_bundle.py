from pikepdf import Pdf , PdfError
import asyncio
import os 


async def pdf_silcer(location,message_id,client,msg,naming):
    with Pdf.open(location,'wb') as pdf:
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
        await msg.edit(text=f'Successfully Uploaded {int(n)+1} files')