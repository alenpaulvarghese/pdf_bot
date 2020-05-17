# idea from https://github.com/SpEcHiDe/AnyDLBot/blob/master/translation.py
class Phrase(object):
    DECRYPT_GUIDE = '<b>Decrypt PDF using the following method</b>\n1. send the pdf file\n2. send the following command as a reply to the pdf file\n<code>/decrypt "passphrase"</code>'
    ENCRYPT_GUIDE = '<b>Encrypt PDF using the following method</b>\n1. send the pdf file\n2. send the following command as a reply to the pdf file\n<code>/encrypt "passphrase"</code>'
    COMPRESS_LOW = '<b>Compress PDF using the following method</b>\n[COMPRESSION RATIO : LOW]\n1. send the pdf file\n2. send the following command as a reply to the pdf file\n<code>/compress low</code>'
    COMPRESS_MEDIUM = '<b>Compress PDF using the following method</b>\n[COMPRESSION RATIO : MEDIUM]\n1. send the pdf file\n2. send the following command as a reply to the pdf file\n<code>/compress medium</code>'
    COMPRESS_HIGH = '<b>Compress PDF using the following method</b>\n[COMPRESSION RATIO : HIGH]\n1. send the pdf file\n2. send the following command as a reply to the pdf file\n<code>/compress high</code>'