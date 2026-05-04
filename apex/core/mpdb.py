import os

from mp_api.client import MPRester
from dflow.python import upload_packages
upload_packages.append(__file__)


web = "materials.org"


def check_apikey():
    try:
        apikey = os.environ["MAPI_KEY"]
    except KeyError:
        print("You have to get a MAPI_KEY from " + web)
        print("and execute following command:")
        print('echo "export MAPI_KEY=yourkey">> ~/.bashrc')
        print("source ~/.bashrc")
        os._exit(0)
    return MPRester(apikey)


def get_structure(mp_id):
    with check_apikey() as mpr:
        try:
            structure = mpr.get_structure_by_material_id(mp_id)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to fetch structure for {mp_id} from Materials Project."
            ) from exc
        if structure is not None:
            return structure
        docs = mpr.materials.summary.search(
            material_ids=[mp_id],
            deprecated=True,
            fields=["material_id", "structure"],
        )
        if docs and docs[0].structure is not None:
            return docs[0].structure
        raise RuntimeError(f"No structure found for {mp_id} from Materials Project.")
