import binascii
import io
import lzma
import os
import pytest
import py7zr.archiveinfo
import py7zr.properties
import py7zr.io

testdata_path = os.path.join(os.path.dirname(__file__), 'data')


@pytest.mark.unit
def test_py7zr_signatureheader():
    header_data = io.BytesIO(b'\x37\x7a\xbc\xaf\x27\x1c\x00\x02\x70\x2a\xb7\x37\xa0\x00\x00\x00\x00\x00\x00\x00\x21'
                             b'\x00\x00\x00\x00\x00\x00\x00\xb9\xb8\xe4\xbf')
    header = py7zr.archiveinfo.SignatureHeader.retrieve(header_data)
    assert header is not None
    assert header.version == (0, 2)
    assert header.nextheaderofs == 160


@pytest.mark.unit
def test_py7zr_mainstreams():
    header_data = io.BytesIO(b'\x04\x06\x00\x01\t0\x00\x07\x0b\x01\x00\x01#\x03\x01\x01\x05]\x00\x00\x00\x02\x0cB\x00'
                             b'\x08\r\x02\t!\n\x01>jb\x08\xce\x9a\xb7\x88\x00\x00')
    pid = header_data.read(1)
    assert pid == py7zr.properties.Property.MAIN_STREAMS_INFO
    streams = py7zr.archiveinfo.StreamsInfo.retrieve(header_data)
    assert streams is not None


@pytest.mark.unit
def test_py7zr_header():
    fp = open(os.path.join(testdata_path, 'solid.7z'), 'rb')
    header_data = io.BytesIO(b'\x01'
                             b'\x04\x06\x00\x01\t0\x00\x07\x0b\x01\x00\x01#\x03\x01\x01\x05]\x00\x00\x00\x02\x0cB\x00'
                             b'\x08\r\x02\t!\n\x01>jb\x08\xce\x9a\xb7\x88\x00\x00'
                             b'\x05\x03\x0e\x01\x80\x11=\x00t\x00e\x00s\x00t\x00\x00\x00t\x00e\x00s\x00t\x001\x00.'
                             b'\x00t\x00x\x00t\x00\x00\x00t\x00e\x00s\x00t\x00/\x00t\x00e\x00s\x00t\x002\x00.\x00t\x00x'
                             b'\x00t\x00\x00\x00\x14\x1a\x01\x00\x04>\xe6\x0f{H\xc6\x01d\xca \x8byH\xc6\x01\x8c\xfa\xb6'
                             b'\x83yH\xc6\x01\x15\x0e\x01\x00\x10\x00\x00\x00 \x00\x00\x00 \x00\x00\x00\x00\x00')
    header = py7zr.archiveinfo.Header.retrieve(fp, header_data, start_pos=32)
    assert header is not None
    assert header.files_info is not None
    assert header.main_streams is not None
    assert header.files_info.numfiles == 3
    assert len(header.files_info.files) == header.files_info.numfiles


@pytest.mark.unit
def test_py7zr_encoded_header():
    fp = open(os.path.join(testdata_path, 'test_5.7z'), 'rb')
    # set test data to buffer that start with Property.ENCODED_HEADER
    buffer = io.BytesIO(b'\x17\x060\x01\tp\x00\x07\x0b\x01\x00\x01#\x03\x01\x01\x05]\x00'
                        b'\x00\x10\x00\x0c\x80\x9d\n\x01\xe5\xa1\xb7b\x00\x00')
    header = py7zr.archiveinfo.Header.retrieve(fp, buffer, start_pos=32)
    assert header is not None
    assert header.files_info is not None
    assert header.main_streams is not None
    assert header.files_info.numfiles == 3
    assert len(header.files_info.files) == header.files_info.numfiles


@pytest.mark.unit
def test_py7zr_files_info():
    header_data = io.BytesIO(b'\x05\x03\x0e\x01\x80\x11=\x00t\x00e\x00s\x00t\x00\x00\x00t\x00e\x00s\x00t\x001\x00.'
                             b'\x00t\x00x\x00t\x00\x00\x00t\x00e\x00s\x00t\x00/\x00t\x00e\x00s\x00t\x002\x00.\x00t\x00x'
                             b'\x00t\x00\x00\x00\x14\x1a\x01\x00\x04>\xe6\x0f{H\xc6\x01d\xca \x8byH\xc6\x01\x8c\xfa\xb6'
                             b'\x83yH\xc6\x01\x15\x0e\x01\x00\x10\x00\x00\x00 \x00\x00\x00 \x00\x00\x00\x00\x00')
    pid = header_data.read(1)
    assert pid == py7zr.properties.Property.FILES_INFO
    files_info = py7zr.archiveinfo.FilesInfo.retrieve(header_data)
    assert files_info is not None
    assert files_info.files[0].get('filename') == 'test'
    assert files_info.files[1].get('filename') == 'test1.txt'
    assert files_info.files[2].get('filename') == 'test/test2.txt'


@pytest.mark.unit
def test_py7zr_files_info2():
    header_data = io.BytesIO(b'\x05\x04\x11_\x00c\x00o\x00p\x00y\x00i\x00n\x00g\x00.\x00t\x00x\x00t\x00\x00\x00H\x00'
                             b'i\x00s\x00t\x00o\x00r\x00y\x00.\x00t\x00x\x00t\x00\x00\x00L\x00i\x00c\x00e\x00n\x00s'
                             b'\x00e\x00.\x00t\x00x\x00t\x00\x00\x00r\x00e\x00a\x00d\x00m\x00e\x00.\x00t\x00x\x00t\x00'
                             b'\x00\x00\x14"\x01\x00\x00[\x17\xe6\xc70\xc1\x01\x00Vh\xb5\xda\xf8\xc5\x01\x00\x97\xbd'
                             b'\xf9\x07\xf7\xc4\x01\x00gK\xa8\xda\xf8\xc5\x01\x15\x12\x01\x00  \x00\x00  \x00'
                             b'\x00  \x00\x00  \x00\x00\x00\x00')
    pid = header_data.read(1)
    assert pid == py7zr.properties.Property.FILES_INFO
    files_info = py7zr.archiveinfo.FilesInfo.retrieve(header_data)
    assert files_info is not None
    assert files_info.numfiles == 4
    assert files_info.files[0].get('filename') == 'copying.txt'
    assert files_info.files[0].get('attributes') == 0x2020
    assert files_info.files[1].get('filename') == 'History.txt'
    assert files_info.files[1].get('attributes') == 0x2020
    assert files_info.files[2].get('filename') == 'License.txt'
    assert files_info.files[2].get('attributes') == 0x2020
    assert files_info.files[3].get('filename') == 'readme.txt'
    assert files_info.files[3].get('attributes') == 0x2020


@pytest.mark.unit
def test_lzma_lzma2_compressor():
    filters = [{'id': 33, 'dict_size': 16777216}]
    assert lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=filters) is not None


@pytest.mark.unit
def test_lzma_lzma2bcj_compressor():
    filters = [{'id': 4}, {'id': 33, 'dict_size': 16777216}]
    assert lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=filters) is not None


@pytest.mark.unit
def test_read_archive_properties():
    buf = io.BytesIO()
    inp = binascii.unhexlify('0207012300')
    buf.write(inp)
    buf.seek(0, 0)
    ap =  py7zr.archiveinfo.ArchiveProperties.retrieve(buf)
    assert ap.property_data[0] == (0x23, )  # FIXME: what should be?



@pytest.mark.unit
def test_write_booleans():
    booleans = [True, False, True, True, False, True, False, False, True]
    buffer = io.BytesIO()
    py7zr.io.write_boolean(buffer, booleans, all_defined=False)
    actual = buffer.getvalue()
    assert actual == b'\xb4\x80'


@pytest.mark.unit
def test_write_booleans2():
    booleans = [True, False, True, True, False, True, False, False, True]
    buffer = io.BytesIO()
    py7zr.io.write_boolean(buffer, booleans, all_defined=True)
    actual = buffer.getvalue()
    assert actual == b'\x00\xb4\x80'


@pytest.mark.unit
def test_write_packinfo():
    packinfo = py7zr.archiveinfo.PackInfo()
    packinfo.packpos = 0x02345678
    packinfo.packsizes = [0x1234, 0x3456, 0x5678]
    buffer = io.BytesIO()
    packinfo.write(buffer)
    actual = buffer.getvalue()
    assert actual == b'\xe2\x34\x56\x78\x03\x09\x92\x34\xb4\x56\xc0\x56\x78\x00'