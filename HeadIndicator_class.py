

class HeadIndicator(gl.GLViewWidget):
    """
    3d model of a head that rotate according to the pupil neon's accelerometer
    """
    def __init__(self):
        super().__init__()
        self.setMaximumWidth(350)

        self.setCameraPosition(distance=130)

        mesh = trimesh.load_mesh("assets/head.obj")
        pink_color = [ 0.921, 0.834, 0.736, 0.5]  # RGBA for pink
        vertices = np.array(mesh.vertices)
        faces = np.array(mesh.faces)

        meshdata = gl.MeshData(vertexes=vertices, faces=faces)
        self.head = gl.GLMeshItem(meshdata=meshdata, smooth=False, color = pink_color, shader="edgeHilight")

        self.head.translate(0, 0, -25)
        self.addItem(self.head)

    @staticmethod
    def quaternion_to_rotation_matrix(w : float, x : float, y : float, z : float):
        """
        Generate a rotation matrix to apply to the head model from the quarternion given by the accelerometer
        
        Returns
        -------
        m4 : np.ndarray
            Rotation matrix to apply to the head to properly follow the movements of the glasses

        """
        m = np.array([[
            1 - 2 * y * y - 2 * z * z, 2 * x * y - 2 * z * w,
            2 * x * z + 2 * y * w
        ],
                      [
                          2 * x * y + 2 * z * w, 1 - 2 * x * x - 2 * z * z,
                          2 * y * z - 2 * x * w
                      ],
                      [
                          2 * x * z - 2 * y * w, 2 * y * z + 2 * x * w,
                          1 - 2 * x * x - 2 * y * y
                      ]])
        flip_y = np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]])
        m = m @ flip_y
        m4 = np.identity(4)
        m4[:3, :3] = m
        return m4

    def onNewData(self, timestamps : list, data : dict):
        """
        receive data from the neon's accelerometer and update the position of the head accordingly. 
        timestamps and data use lists to keep compatibility with the Streamlab version of that indicator. 
        In time the two should either be merged or separeted

        Parameters
        ----------
        timestamps : list
            list of timestamps in unix seconds.
        data : dict
            dict with list of values generated from the pupil neon api accelerometer informations.
        """
        if not timestamps:
            return

        rotation_matrix = self.quaternion_to_rotation_matrix(
            data["quaternion_w"][-1], data["quaternion_x"][-1],
            data["quaternion_y"][-1], data["quaternion_z"][-1])

        translation_matrix = QMatrix4x4()
        translation_matrix.translate(0, 0, -25)

        self.head.setTransform(translation_matrix *
                               QMatrix4x4(*rotation_matrix.flatten()))