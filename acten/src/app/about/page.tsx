import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About ACTEN | Association of Catholic Trained Evangelizers in Nigeria',
  description: 'Learn about ACTEN, our mission, vision, and the organizational structure guiding Catholic evangelization in Nigeria.',
};

export default function AboutPage() {
  return (
    <div className="bg-white">
      <div className="bg-acten-green py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-white">
          <h1 className="text-4xl font-serif font-bold text-acten-gold mb-4">About ACTEN</h1>
          <p className="text-xl max-w-2xl mx-auto">Association of Catholic Trained Evangelizers in Nigeria</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 prose prose-lg">
        <section className="mb-12">
          <h2 className="text-3xl font-serif font-bold text-acten-burgundy mb-6">Mission</h2>
          <p className="text-xl italic border-l-4 border-acten-gold pl-6 py-2 text-gray-700 bg-acten-ivory">
            “To promote the evangelization mission of the Catholic Church in Nigeria by documenting, communicating, and supporting activities that proclaim Jesus Christ, strengthen Christian faith, encourage discipleship, and bring the Gospel to individuals, families, and communities.”
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-3xl font-serif font-bold text-acten-burgundy mb-6">Vision</h2>
          <p className="text-xl italic border-l-4 border-acten-green pl-6 py-2 text-gray-700 bg-acten-ivory">
            “A vibrant community of trained Catholic evangelizers in Nigeria, committed to proclaiming the Gospel, nurturing Christian faith, and witnessing to Christ in every part of society.”
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-3xl font-serif font-bold text-acten-burgundy mb-6">Introduction & Identity</h2>
          <p>
            The Association of Catholic Trained Evangelizers in Nigeria (ACTEN) serves as a national platform dedicated to
            coordinating, supporting, and reporting on the evangelization activities of the Catholic Church across the nation.
          </p>
          <p>
            [Content placeholder: Detailed history and founding information to be provided by ACTEN leadership.]
          </p>
        </section>

        <section className="mb-12">
          <h2 className="text-3xl font-serif font-bold text-acten-burgundy mb-6">National Leadership</h2>
          <div className="bg-acten-ivory p-6 rounded-lg border border-gray-200">
            <p className="text-center text-gray-500 italic">
              Official leadership structures, officers, and chaplaincy details are pending confirmation and will be updated here.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
