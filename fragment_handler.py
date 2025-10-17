import os

def assemble_fragments(fragments, output_file):
    with open(output_file, 'wb') as out:
        for frag in sorted(fragments, key=lambda x: x[0]):
            with open(frag[1], 'rb') as f:
                out.write(f.read())

from fragment_handler import assemble_fragments

# fragments = [(offset1, 'path1.bin'), (offset2, 'path2.bin')]
assemble_fragments(fragments, 'recovered_files/reassembled.jpg')
