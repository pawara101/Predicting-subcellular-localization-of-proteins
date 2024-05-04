import h5py

def fasta_to_h5(fasta_file, h5_file):
    sequences = {}
    current_seq_id = None
    current_seq = ''

    # Parse FASTA file
    with open(fasta_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_seq_id:
                    sequences[current_seq_id] = current_seq
                current_seq_id = line[1:]
                current_seq = ''
            else:
                current_seq += line
        if current_seq_id:
            sequences[current_seq_id] = current_seq

    # Write sequences to HDF5 file
    with h5py.File(h5_file, 'w') as hf:
        for seq_id, seq in sequences.items():
            hf.create_dataset(seq_id, data=seq.encode('utf-8'))

# Example usage
fasta_file = 'test.fasta'
h5_file = 'sequences.h5'
fasta_to_h5(fasta_file, h5_file)
