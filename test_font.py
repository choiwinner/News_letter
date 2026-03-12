import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import koreanize_matplotlib
import networkx as nx
import base64

def test_font_rendering():
    print(f"Current font family: {plt.rcParams['font.family']}")
    
    G = nx.Graph()
    G.add_node("한글노드", type="테스트")
    G.add_node("EnglishNode", type="test")
    G.add_edge("한글노드", "EnglishNode", relation="관계")
    
    pos = nx.spring_layout(G)
    fig, ax = plt.subplots()
    
    nx.draw(G, pos, ax=ax, with_labels=False)
    
    # Try with explicit font_family from rcParams
    font_name = plt.rcParams['font.family'][0] if isinstance(plt.rcParams['font.family'], list) else plt.rcParams['font.family']
    print(f"Attempting to use font: {font_name}")
    
    nx.draw_networkx_labels(G, pos, ax=ax, font_family=font_name)
    
    output = "font_test.png"
    plt.savefig(output)
    print(f"Saved test image to {output}")

if __name__ == "__main__":
    test_font_rendering()
