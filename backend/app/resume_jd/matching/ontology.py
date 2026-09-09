from app.resume_jd.models.phase_04_models import OntologyRelation

class OntologyService:
    def __init__(self):
        # A minimal, conservative in-memory ontology for Data Engineering relationships
        # Keys are tuples of canonical/normalized concepts (lowercase).
        # We store relations in a bidirectional or unidirectional manner.
        self._relations = {
            # EQUIVALENT
            ("k8s", "kubernetes"): OntologyRelation.EQUIVALENT,
            ("kubernetes", "k8s"): OntologyRelation.EQUIVALENT,
            ("gcp", "google cloud"): OntologyRelation.EQUIVALENT,
            ("google cloud", "gcp"): OntologyRelation.EQUIVALENT,
            
            # RELATED
            ("aws glue", "gcp dataflow"): OntologyRelation.RELATED,
            ("gcp dataflow", "aws glue"): OntologyRelation.RELATED,
            ("linux", "ubuntu"): OntologyRelation.RELATED,
            ("ubuntu", "linux"): OntologyRelation.RELATED,
            
            # BROADER / NARROWER (Concept 1 is [Relation] to Concept 2)
            ("python", "pyspark"): OntologyRelation.BROADER,
            ("pyspark", "python"): OntologyRelation.NARROWER,
            
            ("aws", "s3"): OntologyRelation.BROADER,
            ("s3", "aws"): OntologyRelation.NARROWER,
            ("aws", "ec2"): OntologyRelation.BROADER,
            ("ec2", "aws"): OntologyRelation.NARROWER,
        }

    def get_relation(self, concept1: str, concept2: str) -> OntologyRelation:
        """
        Determines the ontological relationship between two concepts.
        Returns UNKNOWN if no specific relationship is defined.
        """
        if not concept1 or not concept2:
            return OntologyRelation.UNKNOWN
            
        c1 = concept1.strip().lower()
        c2 = concept2.strip().lower()
        
        if c1 == c2:
            return OntologyRelation.EQUIVALENT
            
        return self._relations.get((c1, c2), OntologyRelation.UNKNOWN)
