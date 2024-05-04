from bio_embeddings import pipeline  # Import pipeline for working with FASTA files

# Define the path to your FASTA file
fasta_path = "path/to/your/protein.fasta"  # Replace with your actual path

# Create a pipeline object specifying the embedder (other options available)
pipe = pipeline.Pipeline(embedder="ProtTrans")  # ProtTrans is a protein embedding method

# Run the pipeline to process the FASTA file and generate embeddings
pipe.run(fasta_path)

# The pipeline generates embedding files. You can access them using the pipeline object

# Get the path to the main embedding file
embeddings_file = pipe.result_files["embeddings"]

# Get the path to the (optional) reduced embedding file (for visualization)
reduced_embeddings_file = pipe.result_files.get("reduced_embedding", None)

# Now you can use the embedding files for further analysis or visualization tasks

# (Code for further analysis/visualization not included for brevity)
