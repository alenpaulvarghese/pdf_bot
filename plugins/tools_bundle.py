from pikepdf import Pdf , PdfError
import asyncio
import os 


async def pdf_silcer(location,message_id,client):
    with Pdf.open(location,'wb') as pdf:
        for n, page in enumerate(pdf.pages):
                dst = Pdf.new()
                dst.pages.append(page)
                location = (f'{str(message_id)}-{n}.pdf')
                dst.save(location)
                await client.send_document(
                    document=location,
                    chat_id=message_id
                )