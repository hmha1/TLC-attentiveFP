import torch.nn.functional as F


def encode_attentive(model, data):
    # Graph-level molecular representation
    return model.graph_encoder(
        data.x,
        data.edge_index,
        data.edge_attr,
        data.batch
    )


def encode_mpnn(model, data):
    x = F.relu(model.atom_encoder(data.x))

    h = x.unsqueeze(0)

    for _ in range(model.num_steps):
        m = F.relu(
            model.conv(x, data.edge_index, data.edge_attr)
        )

        x, h = model.gru(m.unsqueeze(0), h)
        x = x.squeeze(0)

    return model.pool(
        x, data.batch
    )
