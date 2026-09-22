import os
import matplotlib.pyplot as plt

os.makedirs('docs/equations', exist_ok=True)

equations = [
    {
        'filename': 'docs/equations/pipeline.png',
        'text': r'$\mathrm{Document} \rightarrow \mathrm{Structure\text{-}Aware\ Ext.} \rightarrow \mathrm{Chunking} \rightarrow \mathrm{Titan\ v2\ Embeddings} \rightarrow \mathrm{Hybrid\ Retrieval} \rightarrow \mathrm{Verification} \rightarrow \mathrm{Self\text{-}Correction}$',
        'figsize': (11, 1.2),
        'fontsize': 13,
    },
    {
        'filename': 'docs/equations/chunk_provenance.png',
        'text': r'$c_{\mathrm{id}} = \mathrm{UUID}(d_{\mathrm{id}} \parallel p \parallel \mathrm{index}) \quad \mid \quad \mathrm{Metadata}(c) = \{ d_{\mathrm{id}},\, \mathrm{filename}: F,\, \mathrm{page}: p,\, \mathrm{section}: S,\, c_{\mathrm{id}} \}$',
        'figsize': (10, 1.2),
        'fontsize': 13,
    },
    {
        'filename': 'docs/equations/cosine_similarity.png',
        'text': r'$\cos(\mathbf{v}_q, \mathbf{v}_c) = \mathbf{v}_q \cdot \mathbf{v}_c \quad \text{where } \|\mathbf{v}\|_2 = 1$',
        'figsize': (6, 1.2),
        'fontsize': 14,
    },
    {
        'filename': 'docs/equations/hybrid_scoring.png',
        'text': r'$\mathrm{Score}(c, q) = \alpha \cdot \cos(\mathbf{v}_q, \mathbf{v}_c) + (1 - \alpha) \cdot \mathrm{BM25}(c, q) \quad (\alpha = 0.70)$',
        'figsize': (8.5, 1.2),
        'fontsize': 13,
    },
    {
        'filename': 'docs/equations/claim_confidence.png',
        'text': r'$\mathrm{Confidence}(c_i \mid \mathcal{E}) = \max_{e \in \mathcal{E}} \left[ \frac{|\mathrm{Tokens}(c_i) \cap \mathrm{Tokens}(e)|}{|\mathrm{Tokens}(c_i)|} \right]$',
        'figsize': (7, 1.4),
        'fontsize': 14,
    },
    {
        'filename': 'docs/equations/grounding_coverage.png',
        'text': r'$G(A, \mathcal{E}) = \frac{1}{N} \sum_{i=1}^N \mathrm{I}(\mathrm{Confidence}(c_i \mid \mathcal{E}) \geq 0.40)$',
        'figsize': (6.5, 1.4),
        'fontsize': 14,
    },
    {
        'filename': 'docs/equations/query_reformulate.png',
        'text': r'$q_{t+1} = \mathrm{Reformulate}(q_t, \mathcal{U}) \quad \text{where } \mathcal{U} = \{ c_i \mid \text{not grounded} \}$',
        'figsize': (7.5, 1.2),
        'fontsize': 13,
    }
]

for eq in equations:
    fig = plt.figure(figsize=eq['figsize'], dpi=220)
    fig.patch.set_facecolor('#0f172a')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('#0f172a')
    ax.axis('off')
    
    ax.text(0.5, 0.5, eq['text'], color='#38bdf8', fontsize=eq['fontsize'], ha='center', va='center')
    
    plt.savefig(eq['filename'], facecolor='#0f172a', bbox_inches='tight', pad_inches=0.18)
    plt.close(fig)
    print(f'Successfully generated {eq["filename"]}')

print('All 7 math equations rendered successfully!')
