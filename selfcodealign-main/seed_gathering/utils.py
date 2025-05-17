from tree_sitter_parser import LANGUAGE, make_parser, node_to_string
import boto3
from botocore import UNSIGNED
from botocore.config import Config
import smart_open

s3 = boto3.client("s3", config=Config(signature_version=UNSIGNED))
def download_contents(blob_id, src_encoding):
    s3_url = f"s3://softwareheritage/content/{blob_id}"
    with smart_open.open(s3_url, "rb", compression=".gz", transport_params={"client": s3}) as fin:
        content = fin.read().decode(src_encoding)
    
    return content

TOPLEVEL_DOCSTRING_QUERY = LANGUAGE.query("""
(
    (comment) @docstring .
    (function_definition) @function.def
    (#match? @docstring "^/\\\*\\\*\\\n" )                    
)
""")



def parse_ex(parser, ex):
    ex = download_contents(ex["blob_id"], ex["src_encoding"])
    try:
        buf = bytes(ex, "utf8")
        tree = parser.parse(buf)
        return get_fns_with_docstrings(buf, tree)
    except:
        return []
    
def process_chunk(idx_and_chunk):
    parser = make_parser()
    _, chunk = idx_and_chunk
    chunk_new_funs = set()
    for ex in chunk:
        chunk_new_funs.update(parse_ex(parser, ex))
    return chunk_new_funs

def get_fns_with_docstrings(src, tree):
    captures = TOPLEVEL_DOCSTRING_QUERY.captures(tree.root_node)
    res = []
    doc_node = None
    for capture in captures:
        node, ty = capture
        if ty != "function.def":
            doc_node = node
            continue

        # if the starting col is not 0, then it's not a top-level fn
        _, col = node.start_point
        if col != 0:
            continue
        res.append(node_to_string(src, node, doc_node))
        # res.append(node_to_string(src, node))
    return res