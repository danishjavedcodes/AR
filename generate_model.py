import numpy as np
from PIL import Image
import plotly.graph_objects as go
import trimesh
import os

def image_to_obj(image_path, obj_output_path, scale=1.0, height_scale=1.0):
    """
    Converts a 2D grayscale image into a 3D OBJ heightmap model with a 180-degree Y-axis rotation.
    Also returns vertices and faces for further use.

    :param image_path: Path to the input image file.
    :param obj_output_path: File path to save the output OBJ.
    :param scale: Scaling factor for x and y dimensions.
    :param height_scale: Scaling factor for the height (z dimension).
    :return: vertices and faces for visualization/export
    """
    img = Image.open(image_path).convert("L")
    data = np.array(img)
    height, width = data.shape

    vertices = []
    faces = []

    for y in range(height):
        for x in range(width):
            z = data[y, x] * height_scale
            vx = x * scale
            vy = y * scale
            # Apply 180° Y-axis rotation: (x, y, z) → (-x, y, -z)
            vertices.append((-vx, vy, -z))

    for y in range(height - 1):
        for x in range(width - 1):
            v0 = y * width + x
            v1 = y * width + (x + 1)
            v2 = (y + 1) * width + (x + 1)
            v3 = (y + 1) * width + x

            # Two triangles: v0->v1->v2 and v0->v2->v3
            faces.append((v0 + 1, v1 + 1, v2 + 1))  # OBJ uses 1-based indexing
            faces.append((v0 + 1, v2 + 1, v3 + 1))

    with open(obj_output_path, 'w') as f:
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for face in faces:
            f.write(f"f {face[0]} {face[1]} {face[2]}\n")

    print(f"OBJ file saved to: {obj_output_path}")
    return np.array(vertices), np.array(faces) - 1  # Convert to 0-based indexing

def save_as_gltf(vertices, faces, output_path):
    """
    Saves the mesh as a .glb (binary glTF) file using trimesh.

    :param vertices: Nx3 array of vertex positions.
    :param faces: Mx3 array of triangle indices.
    :param output_path: Path to save the .glb file.
    """
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.export(output_path)
    print(f"GLB file saved to: {output_path}")

def visualize_mesh(vertices, faces):
    """
    Visualizes a 3D mesh using Plotly.

    :param vertices: Array of 3D vertex positions.
    :param faces: Array of triangle indices.
    """
    x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
    i, j, k = faces[:, 0], faces[:, 1], faces[:, 2]

    fig = go.Figure(data=[
        go.Mesh3d(
            x=x, y=y, z=z,
            i=i, j=j, k=k,
            color='lightgrey',
            opacity=1.0,
            flatshading=True
        )
    ])
    fig.update_layout(
        title="3D OBJ/GLB Heightmap from Image",
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data',
        ),
        margin=dict(l=0, r=0, b=0, t=30)
    )
    fig.show()

def image_to_colored_glb(image_path, output_glb_path, texture_output_path, scale=1.0, height_scale=1.0):
    """
    Converts a 2D image into a 3D GLB model with heightmap and texture.
    First converts to OBJ, then to GLB, and visualizes the result.

    :param image_path: Path to the input image file
    :param output_glb_path: Path to save the output GLB file
    :param texture_output_path: Path to save the texture
    :param scale: Scaling factor for x and y dimensions
    :param height_scale: Scaling factor for the height (z dimension)
    """
    # First convert to OBJ
    obj_output_path = os.path.splitext(output_glb_path)[0] + '.obj'
    vertices, faces = image_to_obj(image_path, obj_output_path, scale, height_scale)
    
    # Then convert to GLB
    save_as_gltf(vertices, faces, output_glb_path)
    
    # Visualize the result
    visualize_mesh(vertices, faces)
    
    return vertices, faces

if __name__ == "__main__":
    # Example usage
    input_image = "test.png"
    output_glb = "output.glb"
    texture_path = "texture.png"
    
    vertices, faces = image_to_colored_glb(
        input_image, 
        output_glb, 
        texture_path,
        scale=1.0,
        height_scale=1.0
    )
